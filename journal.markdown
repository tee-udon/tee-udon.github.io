---
layout: page
title: Journal
permalink: /photography/journal/
published: false
---

<p class="back-link"><a href="{{ '/photography/' | relative_url }}">← Photography</a></p>

<p class="journal-intro">A more casual companion to the curated projects — a photo or a few from a day, with whatever I want to say about them underneath.</p>

{% assign recent = site.journal | sort: "date" | reverse %}

{% if recent.size == 0 %}
  <p><em>No entries yet.</em></p>
{% else %}
  {% for entry in recent limit: 10 %}
    <article class="journal-feed-entry">
      {% include journal_day.html entry=entry linked=true %}
    </article>
    {% unless forloop.last %}<hr class="journal-feed-divider">{% endunless %}
  {% endfor %}
{% endif %}

<style>
  .back-link {
    margin-bottom: 24px;
    font-size: 0.95em;
  }

  .journal-intro {
    color: #555;
    margin-bottom: 40px;
  }

  .journal-feed-entry {
    margin-bottom: 40px;
  }

  .journal-feed-divider {
    border: 0;
    border-top: 1px solid #eee;
    margin: 50px 0;
  }

  .journal-day-header {
    margin-bottom: 24px;
  }

  .journal-day-header time {
    display: block;
    color: #888;
    font-size: 0.95em;
    margin-bottom: 4px;
  }

  .journal-day-header time a,
  .journal-day-title a {
    color: inherit;
    text-decoration: none;
  }

  .journal-day-header time a:hover,
  .journal-day-title a:hover {
    text-decoration: underline;
  }

  .journal-day-title {
    margin: 0;
    font-size: 1.6em;
  }

  .journal-section {
    margin-bottom: 32px;
  }

  .journal-section-title {
    font-size: 1.15em;
    margin: 0 0 12px;
    font-weight: 600;
  }

  .journal-photos {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
    margin-bottom: 16px;
  }

  .journal-photos[data-count="1"] {
    grid-template-columns: 1fr;
  }

  .journal-photos[data-count="1"] .journal-photo img {
    height: auto;
    max-height: 500px;
  }

  .journal-photo img {
    width: 100%;
    height: 240px;
    object-fit: cover;
    display: block;
  }

  .image-wrapper {
    position: relative;
    display: block;
    width: 100%;
  }

  .shield {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10;
  }

  img {
    -webkit-user-drag: none;
    user-drag: none;
    -webkit-user-select: none;
    user-select: none;
  }

  .journal-caption {
    color: #333;
    line-height: 1.6;
  }

  .journal-caption p {
    margin: 0 0 12px;
  }

  .journal-caption p:last-child {
    margin-bottom: 0;
  }
</style>

<script>
  document.addEventListener('contextmenu', function(e) {
    if (e.target.tagName === 'IMG') {
      e.preventDefault();
    }
  });
</script>
