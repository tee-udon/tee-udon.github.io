---
layout: page
title: Photography
permalink: /photography/
---

<!-- Short intro goes here. Edit freely. -->
My parents always believed that education is the key to a successful life. I remember when my dad took me, as a young kid, to a planetarium, which forever inspired me to try to understand the enigma of space and time relativity. Or when my mom bought me expensive biology textbooks — even when she didn't have a lot herself — because she knew I was deeply interested in understanding how life worked. Because of these educational gifts they had given me, I felt that everything in life could be explained by scientific theories and mathematical equations.

But not everything in life can be explained by logic. Connecting with strangers. Running into them again on the train. Losing friends to distance and time. Losing love to emotional unavailability. Putting in effort in a relationship even when it feels difficult. These are things no textbook could have ever prepared me for. I take these photos because I don't want to forget — the strangers who felt like old friends, the ordinary days with friends that turned out to matter, and the moments I knew I'd lose the second they were over.

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
