// Like 버튼
document.querySelectorAll('.like-btn').forEach(button=>{
    button.addEventListener('click', ()=>{
        const postId = button.dataset.id;
        fetch(`/posts/${postId}/like/`,{
            method:'POST',
            headers:{'X-CSRFToken': getCookie('csrftoken')}
        }).then(r=>r.json()).then(data=>{
            button.querySelector('.like-count').textContent = data.likes_count;
        });
    });
});

// 댓글폼
const commentForm = document.getElementById('comment-form');
if(commentForm){
    commentForm.addEventListener('submit', e=>{
        e.preventDefault();
        const postId = window.location.pathname.split('/')[2];
        const content = commentForm.querySelector('input[name="content"]').value;
        fetch(`/posts/${postId}/comment/`,{
            method:'POST',
            headers:{'X-CSRFToken': getCookie('csrftoken')},
            body: new URLSearchParams({content})
        }).then(r=>r.json()).then(()=>location.reload());
    });
}

// 스토리 슬라이드
let storyIndex = 0;
const stories = document.querySelectorAll('.story-card');
if(stories.length>0){
    showStory(storyIndex);
    document.getElementById('prev-story').addEventListener('click', ()=>{ storyIndex--; showStory(storyIndex); });
    document.getElementById('next-story').addEventListener('click', ()=>{ storyIndex++; showStory(storyIndex); });
    function showStory(index){
        if(index<0) index=stories.length-1;
        if(index>=stories.length) index=0;
        stories.forEach((s,i)=>s.style.display=(i===index?'block':'none'));
        storyIndex=index;
    }
}

// CSRF helper
function getCookie(name){
    let cookieValue=null;
    if(document.cookie && document.cookie!==''){
        const cookies = document.cookie.split(';');
        for(let i=0;i<cookies.length;i++){
            const cookie = cookies[i].trim();
            if(cookie.startsWith(name+'=')){
                cookieValue = decodeURIComponent(cookie.substring(name.length+1));
                break;
            }
        }
    }
    return cookieValue;
}
