---
permalink: /
redirect_from:
  - /about/
  - /about.html
---

<section id="about-me" aria-labelledby="about-heading">
  <h1 id="about-heading">About Me</h1>
  <p>I'm a PhD student at Tsinghua University, working on <strong>vision-language models</strong>, <strong>generalist agents</strong>, and <strong>image generation</strong>. My research includes geometric perception, the evaluation of language agents, and image synthesis with transparency.</p>
  <p>Across these directions, I study how models interpret geometric diagrams, how agents reason and act in interactive environments, and how image generators represent opacity and compose multiple layers. I also explore learnable positional representations for visual models, with a focus on flexibility and generalization across different image resolutions and positional shifts.</p>
</section>

<section id="research" aria-labelledby="research-heading">
  <div class="section-heading">
    <h2 id="research-heading">Selected Research</h2>
    <p class="contribution-note">* Equal contribution</p>
  </div>
  {% assign selected = site.data.publications | where: "section", "selected" %}
  {% for publication in selected %}{% include publication.html publication=publication %}{% endfor %}
</section>

<section id="publications" aria-labelledby="publications-heading">
  <div class="section-heading">
    <h2 id="publications-heading">More Publications</h2>
    <a class="section-link" href="{{ site.author.googlescholar | escape }}">Google Scholar</a>
  </div>
  {% assign publications = site.data.publications | where: "section", "publications" %}
  {% for publication in publications %}{% include publication.html publication=publication %}{% endfor %}
</section>

<section id="collaborations" aria-labelledby="collaborations-heading">
  <div class="section-heading"><h2 id="collaborations-heading">Collaborative Projects</h2></div>
  {% assign projects = site.data.publications | where: "section", "projects" %}
  {% for publication in projects %}{% include publication.html publication=publication %}{% endfor %}
</section>
