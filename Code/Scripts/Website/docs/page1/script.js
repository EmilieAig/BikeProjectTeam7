let slideIndex = 0;
const slides = document.querySelectorAll('.carousel-slide video');
const totalSlides = slides.length;

function showSlide(index) {
  const carouselContainer = document.querySelector('.carousel-container');
  if (index >= totalSlides) slideIndex = 0;
  if (index < 0) slideIndex = totalSlides - 1;
  carouselContainer.style.transform = 'translateX(' + (-slideIndex * 100) + '%)';
}

function nextSlide() {
  slideIndex++;
  showSlide(slideIndex);
}

function prevSlide() {
  slideIndex--;
  showSlide(slideIndex);
}

// Initialiser le carrousel
showSlide(slideIndex);
