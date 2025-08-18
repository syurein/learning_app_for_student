let slideIndex = 0;
const slides = document.querySelectorAll(".slide");

function showSlides() {
    // 全てのスライドを非表示にする
    slides.forEach(slide => {
        slide.style.display = "none";
    });

    // インデックスが範囲外になったら最初/最後に戻す
    if (slideIndex >= slides.length) {
        slideIndex = 0;
    }
    if (slideIndex < 0) {
        slideIndex = slides.length - 1;
    }
    
    // 現在のスライドのみ表示
    if (slides[slideIndex]) {
        slides[slideIndex].style.display = "block";
    }
}

// ボタンのクリックイベント
document.getElementById('nextBtn').addEventListener('click', () => {
    slideIndex++;
    showSlides();
});

document.getElementById('prevBtn').addEventListener('click', () => {
    slideIndex--;
    showSlides();
});

// 初期表示
showSlides();