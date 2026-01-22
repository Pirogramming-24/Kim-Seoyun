from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AIRequest, AIResponse
from .services.huggingface import summarize_text, generate_image, translate_text

def login_required_with_message(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, "gpt/alert_redirect.html", {
                "message": "로그인 후 이용해주세요.",
                "redirect_url": "/login/" 
            })
        return view_func(request, *args, **kwargs)
    return wrapper



# 메인 페이지
@login_required
def index(request):
    return render(request, 'gpt/base.html')


# 이미지 생성 페이지
@login_required_with_message
def image_view(request):
    chat_history = []

    if request.user.is_authenticated:
        requests = AIRequest.objects.filter(user=request.user, task_type="image").order_by("created_at")
        for req in requests:
            chat_history.append({"role": "user", "content": req.input_text})
            if hasattr(req, "response") and req.response.image_base64:
                chat_history.append({"role": "assistant", "content": "", "image": req.response.image_base64})
    else:
        chat_history = request.session.get("image_chat_history", [])

    if request.method == "POST":
        prompt = request.POST.get("prompt", "").strip()
        if not prompt:
            return render(request, "gpt/image.html", {"chat_history": chat_history, "error": "프롬프트를 입력하세요."})

        chat_history.append({"role": "user", "content": prompt})

        image_base64 = generate_image(prompt)
        chat_history.append({"role": "assistant", "content": "", "image": image_base64})
        if request.user.is_authenticated:
            req = AIRequest.objects.create(user=request.user, task_type="image", input_text=prompt)
            AIResponse.objects.create(request=req, image_base64=image_base64, raw_response={"prompt": prompt})
        else:
            request.session["image_chat_history"] = chat_history

    return render(request, "gpt/image.html", {"chat_history": chat_history})

# 요약 페이지
@login_required_with_message
def summarize_view(request):
    chat_history = []

    requests = AIRequest.objects.filter(user=request.user, task_type="summary").order_by("created_at")
    for req in requests:
        chat_history.append({"role": "user", "content": req.input_text})
        if hasattr(req, "response"):
            chat_history.append({"role": "assistant", "content": req.response.output_text})

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if not text:
            return render(request, "gpt/summarize.html", {"chat_history": chat_history, "error": "텍스트를 입력하세요."})


        chat_history.append({"role": "user", "content": text})


        result = summarize_text(text)
        summary = result[0]["summary_text"]
        chat_history.append({"role": "assistant", "content": summary})

        req = AIRequest.objects.create(user=request.user, task_type="summary", input_text=text)
        AIResponse.objects.create(request=req, output_text=summary, raw_response=result)

    return render(request, "gpt/summarize.html", {"chat_history": chat_history})


# 번역 페이지
def translate_view(request):
    if request.user.is_authenticated:
        chat_history = []
        requests = AIRequest.objects.filter(user=request.user, task_type="translate").order_by("created_at")
        for req in requests:
            chat_history.append({"role": "user", "content": req.input_text})
            if hasattr(req, "response"):
                chat_history.append({"role": "assistant", "content": req.response.output_text})

    else:
        chat_history = request.session.get("translate_chat_history", [])
        if request.method == "GET" and request.GET.get("from_post") != "1":
            chat_history = []
            request.session["translate_chat_history"] = []

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if not text:
            return render(request, "gpt/translate.html", {"chat_history": chat_history, "error": "번역할 텍스트를 입력하세요."})

        translated = translate_text(text)

        if request.user.is_authenticated:
            req = AIRequest.objects.create(user=request.user, task_type="translate", input_text=text)
            AIResponse.objects.create(request=req, output_text=translated, raw_response={"input": text, "translated": translated})
            chat_history.append({"role": "user", "content": text})
            chat_history.append({"role": "assistant", "content": translated})
            return render(request, "gpt/translate.html", {"chat_history": chat_history})

        else:
            chat_history.append({"role": "user", "content": text})
            chat_history.append({"role": "assistant", "content": translated})
            request.session["translate_chat_history"] = chat_history
            request.session.modified = True
            return redirect('/gpt/translate/?from_post=1')

    return render(request, "gpt/translate.html", {"chat_history": chat_history})

@login_required
def history_view(request):
    requests = AIRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "gpt/history.html", {"requests": requests})
