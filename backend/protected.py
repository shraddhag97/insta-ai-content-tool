from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from security import verify_token 
from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()

router = APIRouter()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ------------------ Request Schema ------------------ #
class CaptionRequest(BaseModel):
    niche: str
    topic: str
    tone: str


# ------------------ Protected Route ------------------ #
@router.get("/profile")
def profile(user=Depends(verify_token)):
    return {
        "message": "Authenticated",
        "user": user
    }


# ------------------ Generate Caption ------------------ #
@router.post("/generate_caption")
def generate_caption(data: CaptionRequest, user=Depends(verify_token)):

    prompt = f"""
    Generate an Instagram caption.

    Niche: {data.niche}
    Topic: {data.topic}
    Tone: {data.tone}

    Output format:

    Hook (1 sentence)

    Caption (3–4 short lines)

    Call To Action

    10 relevant hashtags
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return {"caption": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------ Generate Reel ------------------ #
@router.post("/generate_reel")
def generate_reel(data: CaptionRequest, user=Depends(verify_token)):

    prompt = f"""
    You are generating a Reel script for Instagram.

    Use EXACTLY the following inputs:

    Niche: {data.niche}
    Topic: {data.topic}
    Tone: {data.tone}

    Do NOT change the niche or topic.

    Output format:

    Hook (first 3 seconds)

    Scene 1

    Scene 2

    Scene 3

    Caption

    10 hashtags related to the niche
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return {"reel_script": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------ Generate Calendar ------------------ #
@router.post("/generate_calendar")
def generate_calendar(data: CaptionRequest, user=Depends(verify_token)):

    prompt = f"""
    You are an Instagram content strategist.

    Create a 7-day Instagram content calendar.

    Inputs:
    Niche: {data.niche}
    Topic: {data.topic}
    Tone: {data.tone}

    Rules:
    - Do NOT change the niche or topic
    - Mix content types (Reel, Carousel, Story, Post)

    Output format:

    Day 1:
    Content Type:
    Idea:

    Day 2:
    Content Type:
    Idea:

    Day 3:
    Content Type:
    Idea:

    Day 4:
    Content Type:
    Idea:

    Day 5:
    Content Type:
    Idea:

    Day 6:
    Content Type:
    Idea:

    Day 7:
    Content Type:
    Idea:
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return {"calendar": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))