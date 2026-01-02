
// Tag filtering and navigation for blog reflection

class ReflectionApp {
  constructor() {
    this.activeFilters = new Set();
    this.data = null;
  }

  async init() {
    // Load data
    const response = await fetch('data/posts.json');
    this.data = await response.json();

    // Setup event listeners
    this.setupTagFilters();
  }

  setupTagFilters() {
    const tagButtons = document.querySelectorAll('.tag');

    tagButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tag = e.target.dataset.tag;

        // Toggle active state
        e.target.classList.toggle('active');

        if (this.activeFilters.has(tag)) {
          this.activeFilters.delete(tag);
        } else {
          this.activeFilters.add(tag);
        }

        this.applyFilters();
      });
    });
  }

  applyFilters() {
    if (this.activeFilters.size === 0) {
      this.showAllPosts();
      return;
    }

    // Get posts matching ALL active tags
    const matchingPosts = this.data.posts.filter(post => {
      return Array.from(this.activeFilters).every(tag =>
        post.labels.map(l => l.toLowerCase()).includes(tag)
      );
    });

    const matchingIds = new Set(matchingPosts.map(p => p.id));

    // Show/hide posts
    document.querySelectorAll('.post-card').forEach(card => {
      if (matchingIds.has(card.dataset.postId)) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });

    // Update month headers
    this.updateMonthHeaders();
  }

  showAllPosts() {
    document.querySelectorAll('.post-card').forEach(card => {
      card.style.display = 'block';
    });

    document.querySelectorAll('.month-section').forEach(section => {
      section.style.display = 'block';
    });
  }

  updateMonthHeaders() {
    document.querySelectorAll('.month-section').forEach(section => {
      const visiblePosts = Array.from(section.querySelectorAll('.post-card'))
        .filter(card => card.style.display !== 'none');

      section.style.display = visiblePosts.length > 0 ? 'block' : 'none';
    });
  }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  const app = new ReflectionApp();
  app.init();
});
