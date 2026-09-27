---
permalink: /
redirect_from:
  - /about/
  - /about.html
---

<section id="about-me" aria-label="About Me">
  <h1 class="visually-hidden">About Me</h1>
  <p>I'm a PhD student at Tsinghua University, working on <strong>vision-language models</strong>, <strong>generalist agents</strong>, and <strong>image generation</strong>. {% include scholar-summary.html %}</p>
</section>

<section id="news" aria-labelledby="news-heading">
  <h2 class="section-title" id="news-heading">🔥 News</h2>
  {% if site.data.news.size > 0 %}
  <ul class="news-list">
    {% for item in site.data.news %}
    <li><em>{{ item.date | escape }}</em>: &nbsp; {{ item.text | markdownify | remove: '<p>' | remove: '</p>' }}</li>
    {% endfor %}
  </ul>
  {% endif %}
</section>

<section id="publications" aria-labelledby="publications-heading">
  <span id="research" class="legacy-anchor" aria-hidden="true"></span>
  <h2 class="section-title" id="publications-heading">📝 Publications</h2>
  {% assign publications = site.data.publications | where: "section", "publications" %}
  {% for publication in publications %}{% if publication.featured %}{% include publication.html publication=publication %}{% endif %}{% endfor %}
  <ul class="publication-list">
    {% for publication in publications %}{% unless publication.featured %}{% include publication.html publication=publication %}{% endunless %}{% endfor %}
  </ul>
</section>

<section id="technical-reports" aria-labelledby="reports-heading">
  <span id="collaborations" class="legacy-anchor" aria-hidden="true"></span>
  <h2 class="section-title" id="reports-heading">📄 Technical Reports</h2>
  <ul class="publication-list">
    {% assign reports = site.data.publications | where: "section", "reports" %}
    {% for publication in reports %}{% include publication.html publication=publication %}{% endfor %}
  </ul>
</section>

<section id="internship" aria-labelledby="internship-heading">
  <h2 class="section-title" id="internship-heading">💻 Internship</h2>
  {% if site.data.internships.size > 0 %}
  <ul class="internship-list">
    {% for item in site.data.internships %}
    <li><em>{{ item.period | escape }}</em>, {% if item.url %}<a href="{{ item.url | escape }}">{{ item.organization | escape }}</a>{% else %}{{ item.organization | escape }}{% endif %}{% if item.team %}, {{ item.team | escape }}{% endif %}{% if item.role %} — {{ item.role | escape }}{% endif %}{% if item.program %} · {{ item.program | escape }}{% endif %}</li>
    {% endfor %}
  </ul>
  {% endif %}
</section>
