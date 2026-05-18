<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:atom="http://www.w3.org/2005/Atom"
  exclude-result-prefixes="atom">

  <xsl:output method="html" encoding="UTF-8" indent="yes" doctype-system="about:legacy-compat"/>

  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <title>Feed · <xsl:value-of select="/atom:feed/atom:title"/></title>
        <style>
          body {
            max-width: 720px;
            margin: 40px auto;
            padding: 0 24px 60px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            color: #333;
            line-height: 1.6;
          }
          .feed-back {
            display: inline-block;
            color: #666;
            font-size: 0.9em;
            text-decoration: none;
            margin-bottom: 20px;
          }
          .feed-back:hover { color: #000; text-decoration: underline; }
          h1 { margin: 0 0 6px; font-size: 1.8em; }
          .feed-subtitle { color: #666; margin: 0 0 32px; }
          .feed-banner {
            background: #f7f7f7;
            border-left: 3px solid #999;
            padding: 16px 20px;
            margin-bottom: 40px;
            font-size: 0.95em;
            color: #444;
          }
          .feed-banner strong { color: #222; }
          .feed-banner a { color: #333; }
          .feed-banner code {
            background: #fff;
            border: 1px solid #ddd;
            padding: 1px 6px;
            border-radius: 3px;
            font-size: 0.95em;
          }
          .entries-heading {
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #888;
            margin: 0 0 20px;
          }
          .entry {
            border-top: 1px solid #eee;
            padding: 24px 0;
          }
          .entry h2 { margin: 0 0 4px; font-size: 1.2em; }
          .entry h2 a { color: #222; text-decoration: none; }
          .entry h2 a:hover { text-decoration: underline; }
          .entry-date {
            display: block;
            color: #888;
            font-size: 0.9em;
            margin-bottom: 10px;
          }
          .entry-summary { color: #555; margin: 0; }
        </style>
      </head>
      <body>
        <a class="feed-back" href="{/atom:feed/atom:link[@rel='alternate']/@href}">← Back to site</a>
        <h1><xsl:value-of select="/atom:feed/atom:title"/></h1>
        <p class="feed-subtitle"><xsl:value-of select="/atom:feed/atom:subtitle"/></p>

        <div class="feed-banner">
          <p style="margin:0 0 8px;"><strong>This is an RSS feed.</strong></p>
          <p style="margin:0;">To subscribe, paste the URL <code>tee-udon.github.io/feed.xml</code> into a feed reader like <a href="https://feedly.com">Feedly</a>, <a href="https://netnewswire.com">NetNewsWire</a>, or <a href="https://www.inoreader.com">Inoreader</a>. New posts will show up there automatically. Or just <a href="/subscribe/">sign up for emails</a>.</p>
        </div>

        <p class="entries-heading">Recent entries</p>
        <xsl:for-each select="/atom:feed/atom:entry">
          <article class="entry">
            <h2>
              <a href="{atom:link/@href}">
                <xsl:value-of select="atom:title"/>
              </a>
            </h2>
            <time class="entry-date">
              <xsl:value-of select="substring(atom:published, 1, 10)"/>
            </time>
            <p class="entry-summary">
              <xsl:value-of select="atom:summary"/>
            </p>
          </article>
        </xsl:for-each>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
