// Obsessive Nutrition — Main JS

function handleSubscribe(e) {
  e.preventDefault();
  const email = e.target.querySelector('input[type="email"]').value;
  const btn = e.target.querySelector('button');
  
  // TODO: replace with actual email service (ConvertKit / MailerLite)
  btn.textContent = 'Sending...';
  btn.disabled = true;
  
  setTimeout(() => {
    btn.textContent = '✓ Check Your Email!';
    e.target.querySelector('input').value = '';
    
    // Store in localStorage so we know they signed up
    localStorage.setItem('subscribed', email);
  }, 1200);
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// Animate elements on scroll
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.book-card, .blog-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});
