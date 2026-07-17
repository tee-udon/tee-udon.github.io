---
layout: page
title: Letterboxd Diary
permalink: /letterboxd/
---

<p class="back-link"><a href="{{ '/' | relative_url }}">← About</a></p>

<p class="letterboxd-intro">What I've been watching lately, pulled from <a href="https://letterboxd.com/teeudon/" target="_blank" rel="noopener">my Letterboxd diary</a>.</p>

<div id="letterboxd-diary" class="letterboxd-diary">
  <p class="letterboxd-status">Loading…</p>
</div>

<style>
  .back-link {
    margin-bottom: 24px;
    font-size: 0.95em;
  }

  .letterboxd-intro {
    color: #555;
    margin-bottom: 40px;
  }

  .letterboxd-entry {
    display: flex;
    flex-direction: row;
    gap: 20px;
    padding: 24px 0;
    border-bottom: 1px solid #eee;
  }

  .letterboxd-entry:first-child {
    padding-top: 0;
  }

  .letterboxd-poster img {
    width: 70px;
    height: 105px;
    display: block;
    border-radius: 4px;
    background: #f4f4f4;
  }

  .letterboxd-title {
    margin: 0 0 4px;
    font-size: 1.15em;
    font-weight: 600;
    line-height: 1.3;
  }

  .letterboxd-title a {
    color: inherit;
    text-decoration: none;
  }

  .letterboxd-title a:hover {
    text-decoration: underline;
  }

  .letterboxd-year {
    font-weight: normal;
    color: #888;
    font-size: 0.8em;
    margin-left: 4px;
  }

  .letterboxd-date {
    color: #888;
    font-size: 0.9em;
    margin-bottom: 6px;
  }

  .letterboxd-rewatch {
    margin-left: 6px;
  }

  .letterboxd-rating {
    color: #086a00;
    font-size: 1.05em;
    letter-spacing: 1px;
  }

  .letterboxd-status {
    color: #888;
  }
</style>

<script>
  (function () {
    var SOURCE = 'https://lb-embed-content.bokonon.dev?username=teeudon';
    var wrap = document.getElementById('letterboxd-diary');

    // Only allow https URLs on Letterboxd's own hosts; anything else is dropped.
    function safeUrl(raw, hosts) {
      if (!raw) return null;
      try {
        var u = new URL(raw, window.location.href);
        if (u.protocol !== 'https:') return null;
        for (var i = 0; i < hosts.length; i++) {
          if (u.hostname === hosts[i] || u.hostname.endsWith('.' + hosts[i])) return u.href;
        }
        return null;
      } catch (e) {
        return null;
      }
    }

    function text(el) {
      return el ? el.textContent.trim() : '';
    }

    function fail() {
      wrap.replaceChildren();
      var p = document.createElement('p');
      p.className = 'letterboxd-status';
      p.textContent = "Couldn't load the diary right now — ";
      var a = document.createElement('a');
      a.href = 'https://letterboxd.com/teeudon/';
      a.target = '_blank';
      a.rel = 'noopener';
      a.textContent = 'view it on Letterboxd';
      p.appendChild(a);
      p.appendChild(document.createTextNode('.'));
      wrap.appendChild(p);
    }

    function attr(el, name) {
      return el ? el.getAttribute(name) : null;
    }

    function buildEntry(entry) {
      var linkHref = safeUrl(
        attr(entry.querySelector('.letterboxd-embed-tc-poster a'), 'href'),
        ['letterboxd.com']
      );
      var imgSrc = safeUrl(
        attr(entry.querySelector('.letterboxd-embed-tc-poster img'), 'src'),
        ['ltrbxd.com']
      );

      var yearEl = entry.querySelector('.letterboxd-embed-tc-year');
      var year = text(yearEl);

      var titleEl = entry.querySelector('.letterboxd-embed-tc-title');
      var title = '';
      if (titleEl) {
        var clone = titleEl.cloneNode(true);
        var nestedYear = clone.querySelector('.letterboxd-embed-tc-year');
        if (nestedYear) nestedYear.remove();
        title = clone.textContent.trim();
      }
      if (!title) return null;

      var rawDate = text(entry.querySelector('.letterboxd-embed-tc-date'));
      var isRewatch = rawDate.indexOf('♺') !== -1;
      var date = rawDate.replace(/♺/g, '').trim();
      var rating = text(entry.querySelector('.letterboxd-embed-tc-rating'));

      var row = document.createElement('div');
      row.className = 'letterboxd-entry';

      if (imgSrc) {
        var posterWrap = document.createElement('div');
        posterWrap.className = 'letterboxd-poster';
        var img = document.createElement('img');
        img.src = imgSrc;
        img.alt = title + ' poster';
        img.loading = 'lazy';
        if (linkHref) {
          var posterLink = document.createElement('a');
          posterLink.href = linkHref;
          posterLink.target = '_blank';
          posterLink.rel = 'noopener';
          posterLink.appendChild(img);
          posterWrap.appendChild(posterLink);
        } else {
          posterWrap.appendChild(img);
        }
        row.appendChild(posterWrap);
      }

      var meta = document.createElement('div');
      meta.className = 'letterboxd-meta';

      var h2 = document.createElement('h2');
      h2.className = 'letterboxd-title';
      if (linkHref) {
        var titleLink = document.createElement('a');
        titleLink.href = linkHref;
        titleLink.target = '_blank';
        titleLink.rel = 'noopener';
        titleLink.textContent = title;
        h2.appendChild(titleLink);
      } else {
        h2.textContent = title;
      }
      if (year) {
        var yearSpan = document.createElement('span');
        yearSpan.className = 'letterboxd-year';
        yearSpan.textContent = year;
        h2.appendChild(yearSpan);
      }
      meta.appendChild(h2);

      if (date) {
        var dateDiv = document.createElement('div');
        dateDiv.className = 'letterboxd-date';
        dateDiv.textContent = date;
        if (isRewatch) {
          var rw = document.createElement('span');
          rw.className = 'letterboxd-rewatch';
          rw.textContent = '· rewatch';
          dateDiv.appendChild(rw);
        }
        meta.appendChild(dateDiv);
      }

      if (rating) {
        var ratingDiv = document.createElement('div');
        ratingDiv.className = 'letterboxd-rating';
        ratingDiv.textContent = rating;
        meta.appendChild(ratingDiv);
      }

      row.appendChild(meta);
      return row;
    }

    fetch(SOURCE)
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.text();
      })
      .then(function (html) {
        // Parsed into an inert document: no scripts run, no images load, no
        // handlers fire. Only plain text and vetted URLs are copied out of it.
        var doc = new DOMParser().parseFromString(html, 'text/html');
        var entries = doc.querySelectorAll('.letterboxd-embed-tc-diary-entry');
        var frag = document.createDocumentFragment();
        for (var i = 0; i < entries.length; i++) {
          var built = buildEntry(entries[i]);
          if (built) frag.appendChild(built);
        }
        if (!frag.childNodes.length) return fail();
        wrap.replaceChildren(frag);
      })
      .catch(fail);
  })();
</script>
