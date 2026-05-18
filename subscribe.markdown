---
layout: page
title: Subscribe
permalink: /subscribe/
---

<p class="subscribe-intro">Occasional updates when I publish a new photography project or journal entry. No spam, unsubscribe anytime.</p>

<form
  action="https://buttondown.com/api/emails/embed-subscribe/tee-udon"
  method="post"
  target="popupwindow"
  onsubmit="window.open('https://buttondown.com/tee-udon', 'popupwindow')"
  class="subscribe-form"
>
  <label for="bd-email" class="visually-hidden">Email address</label>
  <input
    type="email"
    name="email"
    id="bd-email"
    placeholder="you@example.com"
    required
  />
  <button type="submit">Subscribe</button>
</form>

<p class="subscribe-rss">
  Use a feed reader? Add <code>tee-udon.github.io/feed.xml</code> to it &mdash; or <a href="{{ '/feed.xml' | relative_url }}">open the feed</a>.
</p>

<style>
  .subscribe-intro {
    color: #555;
    margin-bottom: 32px;
    max-width: 560px;
  }

  .subscribe-form {
    display: flex;
    gap: 8px;
    max-width: 480px;
    margin-bottom: 24px;
  }

  .subscribe-form input[type="email"] {
    flex: 1;
    padding: 10px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font: inherit;
    font-size: 1em;
  }

  .subscribe-form input[type="email"]:focus {
    outline: none;
    border-color: #888;
  }

  .subscribe-form button {
    padding: 10px 18px;
    border: 1px solid #333;
    background: #333;
    color: #fff;
    border-radius: 4px;
    font: inherit;
    font-size: 1em;
    cursor: pointer;
    transition: background 0.15s ease, border-color 0.15s ease;
  }

  .subscribe-form button:hover {
    background: #000;
    border-color: #000;
  }

  .subscribe-rss {
    color: #666;
    font-size: 0.95em;
  }

  .visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
  }

  @media (max-width: 480px) {
    .subscribe-form {
      flex-direction: column;
    }
  }
</style>
