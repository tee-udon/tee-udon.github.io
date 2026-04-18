---
layout: page
title: Photography
permalink: /photography/
---

<!-- Short intro goes here. Edit freely. -->
A collection of ongoing photography projects.

{% assign projects = site.photography | sort: "order" %}

<div class="project-grid">
  {% for project in projects %}
  <a href="{{ project.url | relative_url }}" class="project-card">
    <div class="project-cover">
      <img src="/assets/photography_lowres/{{ project.cover }}" alt="{{ project.title }}">
    </div>
    <h2 class="project-title">{{ project.title }}</h2>
    {% if project.blurb %}<p class="project-blurb">{{ project.blurb }}</p>{% endif %}
  </a>
  {% endfor %}
</div>

<style>
  .project-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 30px;
    margin-top: 40px;
  }

  .project-card {
    display: block;
    color: inherit;
    text-decoration: none;
    border: 1px solid #eee;
    border-radius: 4px;
    overflow: hidden;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }

  .project-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    text-decoration: none;
  }

  .project-cover img {
    width: 100%;
    height: 220px;
    object-fit: cover;
    display: block;
  }

  .project-title {
    margin: 16px 16px 8px;
    font-size: 1.25em;
  }

  .project-blurb {
    margin: 0 16px 16px;
    color: #555;
    font-size: 0.95em;
  }
</style>
