---
layout: page
title: Capturing Human Connection
permalink: /photography/
---
> "Loving is so short, forgetting is so long."
>
> <cite>— Pablo Neruda</cite>

I used to live anywhere but the present. My mind was either stuck in the past, dissecting old mistakes, or racing toward an uncertain future, worrying about my experiments or student loans. These thoughts were a constant background noise that made it hard to find joy.

That changed when I started walking San Francisco.

From the slopes of Mission Dolores to the shores of Ocean Beach, I tried to capture the city's beauty with my camera. But when I reviewed my photos, I noticed something surprising: it wasn't the landscapes that moved me, but the people inhabiting them. The city’s hills and streets were merely conduits for human connection.

I view life as an integral—a sum of infinite, small moments. We often worry so much about the "area under the curve" that we miss the beauty of the small slices itself. Photography forces me to slow down, listen to my surroundings, and capture the fleeting, mundane, and beautiful evidence of us connecting with one another.

{% assign featured_photos = site.data.photography | where: "featured", true %}

{% if featured_photos.size > 0 %}
  <h2 style="margin-top: 40px;">Selected Moments</h2>
  <div class="photo-grid" id="featured-grid-container" style="margin-bottom: 50px;">
    {% for photo in featured_photos %}
    <div class="photo-item">
      <div class="image-wrapper">
        <img src="/assets/photography_lowres/{{ photo.filename }}" alt="{{ photo.location }}">
        <div class="shield"></div>
      </div>
      <div class="caption">
        <p>
          {{ photo.location }}<br>
          {{ photo.date }}
        </p>
      </div>
    </div>
    {% endfor %}
  </div>
  <hr> {% endif %}

<h2 style="margin-top: 40px;">All Moments</h2>

<div class="sort-controls" style="text-align: right; margin-bottom: 20px;">
  <label for="sort-select">Sort by: </label>
  <select id="sort-select">
    <option value="newest" selected>Newest First</option>
    <option value="oldest">Oldest First</option>
  </select>
</div>

<div class="photo-grid" id="photo-grid-container">
  {% for photo in site.data.photography %}
  <div class="photo-item" data-timestamp="{{ photo.date | date: '%s' }}">
    <div class="image-wrapper">
      <img src="/assets/photography_lowres/{{ photo.filename }}" alt="{{ photo.location }}">
      <div class="shield"></div>
    </div>
    
    <div class="caption">
      <p>
        {{ photo.location }}<br>
        {{ photo.date }}
      </p>
    </div>
  </div>
  {% endfor %}
</div>


<style>
  .photo-grid {
  column-count: 3; /* Creates 3 columns */
  column-gap: 15px; /* Space between columns */
}

/* Individual photo items */
    .photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.photo-item img {
  width: 100%;
  height: 250px;       /* FORCE a specific height */
  object-fit: cover;   /* This is the magic: it crops instead of stretching */
  display: block;
}

.image-wrapper {
  position: relative; /* Needed to position the shield */
  display: block;      /* Changed from inline-block to block */
  width: 100%;         /* Forces the wrapper to fill the column width */
}

.shield {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0); /* Completely transparent */
  z-index: 10; /* sits on top of the image */
}

img {
  /* Prevent dragging the image */
  -webkit-user-drag: none;
  -khtml-user-drag: none;
  -moz-user-drag: none;
  -o-user-drag: none;
  user-drag: none;

  /* Prevent highlighting the image */
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -o-user-select: none;
  user-select: none;
}
</style>

<script>
  // Disable right-click on all images
  document.addEventListener('contextmenu', function(e) {
    if (e.target.tagName === 'IMG') {
      e.preventDefault();
    }
  });
</script>
<script>
  document.addEventListener('DOMContentLoaded', function() {
    const select = document.getElementById('sort-select');
    const grid = document.getElementById('photo-grid-container');
    
    // Check if the grid exists to prevent errors
    if (!grid) return; 

    // Get all photo items as an array
    const items = Array.from(grid.querySelectorAll('.photo-item'));
    
    // Store original elements in their exact starting order
    const originalOrder = [...items];

    select.addEventListener('change', function() {
      const order = this.value;
      
      if (order === 'original') {
        // Clear grid and restore original order
        grid.innerHTML = '';
        originalOrder.forEach(item => grid.appendChild(item));
        return;
      }

      // Sort the items mathematically based on the timestamp
      items.sort((a, b) => {
        const timeA = parseInt(a.getAttribute('data-timestamp'), 10);
        const timeB = parseInt(b.getAttribute('data-timestamp'), 10);

        if (order === 'newest') {
          return timeB - timeA; // Highest number (newest) first
        } else if (order === 'oldest') {
          return timeA - timeB; // Lowest number (oldest) first
        }
      });

      // Clear the grid and append the sorted items
      grid.innerHTML = '';
      items.forEach(item => grid.appendChild(item));
    });

    // NEW LINE: Trigger the sorting logic immediately when the page loads
    select.dispatchEvent(new Event('change'));
  });
</script>