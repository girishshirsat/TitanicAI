import os
from dotenv import load_dotenv
load_dotenv()
import io
import base64
import json
import re
from typing import Optional

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from groq import Groq
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI(title="TitanicAI Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_csv("Titanic-Dataset.csv")

SESSIONS: dict[str, InMemoryChatMessageHistory] = {}

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))


def get_dataset_context(question: str) -> str:
    """Dynamically compute relevant dataset facts based on the question."""
    q = question.lower()
    context_parts = []

    
    context_parts.append(f"""FULL DATASET FACTS (use these to answer):
- Total passengers: {len(df)}
- Columns available: {', '.join(df.columns.tolist())}
- Survived: {df['Survived'].sum()} ({df['Survived'].mean()*100:.1f}%)
- Male: {(df['Sex']=='male').sum()}, Female: {(df['Sex']=='female').sum()}
- Avg age: {df['Age'].mean():.1f} yrs, Min: {df['Age'].min()}, Max: {df['Age'].max()}
- Avg fare: ${df['Fare'].mean():.2f}
- Pclass 1: {(df['Pclass']==1).sum()}, Pclass 2: {(df['Pclass']==2).sum()}, Pclass 3: {(df['Pclass']==3).sum()}
- Embarked S: {(df['Embarked']=='S').sum()}, C: {(df['Embarked']=='C').sum()}, Q: {(df['Embarked']=='Q').sum()}
- Male survival: {df[df['Sex']=='male']['Survived'].mean()*100:.1f}%, Female survival: {df[df['Sex']=='female']['Survived'].mean()*100:.1f}%""")

    # Names list questions
    if any(w in q for w in ['name', 'list', 'who', 'passenger']):
        if 'male' in q and 'female' not in q:
            names = df[df['Sex']=='male']['Name'].tolist()
            context_parts.append(f"\nALL MALE PASSENGER NAMES ({len(names)} total):\n" + "\n".join(f"- {n}" for n in names))
        elif 'female' in q and 'male' not in q:
            names = df[df['Sex']=='female']['Name'].tolist()
            context_parts.append(f"\nALL FEMALE PASSENGER NAMES ({len(names)} total):\n" + "\n".join(f"- {n}" for n in names))
        elif 'male' in q and 'female' in q:
            males = df[df['Sex']=='male'][['Name']].copy()
            males['Gender'] = 'Male'
            females = df[df['Sex']=='female'][['Name']].copy()
            females['Gender'] = 'Female'
            combined = pd.concat([males, females])
            context_parts.append(f"\nALL PASSENGER NAMES WITH GENDER:\n{combined.to_string(index=False)}")
        elif any(w in q for w in ['all', 'every', 'passengers']):
            context_parts.append(f"\nALL PASSENGER NAMES:\n" + "\n".join(f"- {n}" for n in df['Name'].tolist()))

    # Age group questions
    age_match = re.search(r'(\d+)\s*[-to]+\s*(\d+)', q)
    if age_match or any(w in q for w in ['age group', 'age range', 'years old', 'aged']):
        if age_match:
            age_min, age_max = int(age_match.group(1)), int(age_match.group(2))
            subset = df[(df['Age'] >= age_min) & (df['Age'] <= age_max)]
            if 'male' in q:
                subset = subset[subset['Sex'] == 'male']
            elif 'female' in q:
                subset = subset[subset['Sex'] == 'female']
            context_parts.append(f"\nPASSENGERS AGED {age_min}-{age_max} ({'Male' if 'male' in q else 'Female' if 'female' in q else 'All genders'}):")
            context_parts.append(f"Count: {len(subset)}")
            context_parts.append(f"Names:\n" + "\n".join(f"- {row['Name']} (Age: {row['Age']}, Sex: {row['Sex']})" for _, row in subset.iterrows()))
        else:
            age_groups = pd.cut(df['Age'].dropna(), bins=[0,10,20,30,40,50,60,70,80], labels=['0-10','11-20','21-30','31-40','41-50','51-60','61-70','71-80'])
            context_parts.append(f"\nAGE GROUP DISTRIBUTION:\n{age_groups.value_counts().sort_index().to_string()}")

    # Survival specific queries
    if any(w in q for w in ['surviv', 'died', 'dead', 'alive']):
        surv_data = df.groupby(['Sex', 'Pclass'])['Survived'].agg(['sum', 'count', 'mean']).reset_index()
        surv_data.columns = ['Sex', 'Pclass', 'Survived', 'Total', 'Rate']
        surv_data['Rate'] = (surv_data['Rate'] * 100).round(1)
        context_parts.append(f"\nSURVIVAL BREAKDOWN BY SEX & CLASS:\n{surv_data.to_string(index=False)}")

    # Fare questions
    if any(w in q for w in ['fare', 'ticket', 'price', 'cost', 'paid']):
        context_parts.append(f"\nFARE STATISTICS:\nMin: ${df['Fare'].min():.2f}, Max: ${df['Fare'].max():.2f}, Median: ${df['Fare'].median():.2f}")
        context_parts.append(f"By class:\n{df.groupby('Pclass')['Fare'].mean().apply(lambda x: f'${x:.2f}').to_string()}")

    # Class questions
    if any(w in q for w in ['class', 'pclass', '1st', '2nd', '3rd', 'first', 'second', 'third']):
        context_parts.append(f"\nCLASS BREAKDOWN:\n{df.groupby('Pclass').agg(Count=('PassengerId','count'), Survived=('Survived','sum'), SurvivalRate=('Survived','mean')).assign(SurvivalRate=lambda x: (x['SurvivalRate']*100).round(1)).to_string()}")

    return "\n".join(context_parts)


def build_system_prompt(question: str) -> str:
    dataset_context = get_dataset_context(question)
    return f"""You are TitanicAI, an expert data analyst for the Titanic dataset. You have FULL access to all passenger data.

{dataset_context}

IMPORTANT RULES:
1. You MUST answer every question using the data provided above. Never say you don't have access.
2. For name lists: format them as a clean markdown table with columns like | Name | Gender | Age | etc.
3. For counts/stats: always give the exact number from the data.
4. For age groups: use the exact passenger data provided.
5. Remember the full conversation history and refer to it accurately when asked.
6. If asked what a previous question was, look at the conversation history and answer correctly.
7. For visualizations, include exactly one JSON block like:
<chart>
{{"type": "histogram|bar|pie|scatter|box", "column": "ColumnName", "title": "Chart Title", "group_by": "OptionalColumn"}}
</chart>

Be direct, accurate, and helpful. Use markdown tables for list data."""


def get_or_create_session(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in SESSIONS:
        SESSIONS[session_id] = InMemoryChatMessageHistory()
    return SESSIONS[session_id]


def build_messages(question: str, history: InMemoryChatMessageHistory) -> list:
    system_prompt = build_system_prompt(question)
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history.messages:
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})
    messages.append({"role": "user", "content": question})
    return messages


def generate_chart(chart_spec: dict) -> Optional[str]:
    try:
        chart_type = chart_spec.get("type", "bar")
        column = chart_spec.get("column", "")
        title = chart_spec.get("title", "")
        group_by = chart_spec.get("group_by", None)

        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor("#0a0f2c")
        ax.set_facecolor("#0d1340")
        colors = ["#00d4ff", "#7c3aed", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6"]

        if column not in df.columns and chart_type != "bar":
            return None

        if chart_type == "histogram":
            data = df[column].dropna()
            ax.hist(data, bins=25, color="#00d4ff", edgecolor="#0a0f2c", alpha=0.85)
            ax.set_xlabel(column, color="white")
            ax.set_ylabel("Count", color="white")

        elif chart_type == "bar":
            if group_by and group_by in df.columns:
                counts = df.groupby(group_by)[column].mean() if column in df.columns else df[group_by].value_counts()
            elif column in df.columns:
                counts = df[column].value_counts()
            else:
                counts = df.iloc[:, 0].value_counts()
            bars = ax.bar(counts.index.astype(str), counts.values, color=colors[:len(counts)], edgecolor="#0a0f2c")
            ax.set_xlabel(column, color="white")
            ax.set_ylabel("Count", color="white")
            for bar, val in zip(bars, counts.values):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                        f"{val:.1f}" if isinstance(val, float) else f"{val}",
                        ha="center", va="bottom", color="white", fontsize=9)

        elif chart_type == "pie":
            counts = df[column].value_counts()
            wedges, texts, autotexts = ax.pie(
                counts.values, labels=counts.index, autopct="%1.1f%%",
                colors=colors[:len(counts)], startangle=140,
                textprops={"color": "white"}
            )
            for at in autotexts:
                at.set_color("white")

        elif chart_type == "scatter":
            x_col = column
            y_col = group_by if group_by and group_by in df.columns else "Fare"
            data = df[[x_col, y_col, "Survived"]].dropna()
            ax.scatter(data[x_col], data[y_col],
                       c=data["Survived"].map({0: "#ef4444", 1: "#10b981"}),
                       alpha=0.6, s=30)
            ax.set_xlabel(x_col, color="white")
            ax.set_ylabel(y_col, color="white")

        elif chart_type == "box":
            if group_by and group_by in df.columns:
                groups = [df[df[group_by] == val][column].dropna() for val in df[group_by].unique()]
                labels = df[group_by].unique().astype(str)
            else:
                groups = [df[column].dropna()]
                labels = [column]
            bp = ax.boxplot(groups, labels=labels, patch_artist=True)
            for patch, color in zip(bp["boxes"], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            ax.set_ylabel(column, color="white")

        ax.set_title(title, color="#00d4ff", fontsize=13, fontweight="bold", pad=12)
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#1e2a5e")

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=110, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception as e:
        print(f"Chart error: {e}")
        return None


def extract_chart_spec(text: str) -> tuple[str, Optional[dict]]:
    pattern = r"<chart>(.*?)</chart>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        try:
            spec = json.loads(match.group(1).strip())
            clean_text = re.sub(pattern, "", text, flags=re.DOTALL).strip()
            return clean_text, spec
        except json.JSONDecodeError:
            pass
    return text, None


class ChatRequest(BaseModel):
    session_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    chart_base64: Optional[str] = None
    session_id: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    history = get_or_create_session(request.session_id)
    messages = build_messages(request.question, history)

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2,
            max_tokens=2048,
        )
        raw_response = completion.choices[0].message.content
        answer, chart_spec = extract_chart_spec(raw_response)

        history.add_user_message(request.question)
        history.add_ai_message(answer)

        chart_b64 = generate_chart(chart_spec) if chart_spec else None

        return ChatResponse(
            answer=answer.strip(),
            chart_base64=chart_b64,
            session_id=request.session_id,
        )
    except Exception as e:
        return ChatResponse(
            answer=f"I encountered an error: {str(e)}",
            session_id=request.session_id,
        )


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    if session_id in SESSIONS:
        del SESSIONS[session_id]
    return {"message": "Session cleared"}


@app.get("/health")
async def health():
    return {"status": "ok", "passengers": len(df)}


@app.get("/dataset/summary")
async def dataset_summary():
    return {
        "total_passengers": len(df),
        "survival_rate": round(df["Survived"].mean() * 100, 2),
        "male_pct": round((df["Sex"] == "male").mean() * 100, 2),
        "female_pct": round((df["Sex"] == "female").mean() * 100, 2),
        "avg_age": round(df["Age"].mean(), 1),
        "avg_fare": round(df["Fare"].mean(), 2),
    }