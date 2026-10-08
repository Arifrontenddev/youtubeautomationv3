// YouTube Agent Automation Studio — Interactive Client Logic
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initDashboard();
  initHookAndScript();
  initPackagingLinter();
  initEditDecisionList();
  initChaptersBuilder();
  initShortsExtractor();
  initSeoGenerator();
  initRetentionRadar();
  initViralOutliers();
  initCommentManager();
  initChannelAuditAndPlan();
  initVoiceProfile();
});

// Toast Notifications
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✅' : '⚠️'}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Navigation & Tab Switching
function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  const tabPanes = document.querySelectorAll('.tab-pane');
  const heading = document.getElementById('page-heading');
  const subheading = document.getElementById('page-subheading');

  const titles = {
    'tab-dashboard': ['Mission Control', 'End-to-End YouTube Automation Pipeline & Agent Suite'],
    'tab-script': ['Hook & Script Lab', '21 Hook Formulas, Heuristic Scoring & Retention-Engineered Beats'],
    'tab-package': ['Packaging & Linter', 'Title & Thumbnail Pairing Linter with Live Search & Feed Previews'],
    'tab-edit': ['Edit Decision List', 'Detect Dead-Air Gaps, Filler Words & Restart Retakes from Transcript'],
    'tab-chapters': ['Chapters Builder', 'Auto-Segment Transcripts into YouTube-Validated Description Chapters'],
    'tab-shorts': ['Shorts Extractor', 'Find High-Retention Short-Form Clips with Newly Engineered Opening Hooks'],
    'tab-seo': ['SEO & Metadata', 'Generate Search-Winning Descriptions, Queries, and Optimized Tags'],
    'tab-retention': ['Retention Radar', 'Diagnose Hook Leaks (0-30s), Cliff Drops & Middle Bleed Rates'],
    'tab-viral': ['Viral Outlier Radar', 'Rank Niche Outliers by Multiple Over Channel Median'],
    'tab-comment': ['Comment Manager', '4-Pile Triage, Voice-Matched Replies & Pinned Comment Selector'],
    'tab-audit': ['Audit & Weekly Plan', 'Single-Fix Channel Bottleneck & Hours-Matched Production Schedule'],
    'tab-voice': ['Creator Voice Profile', 'Configure Tone, Audience, Persona and Taboo Words in voice.md']
  };

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetTab = item.getAttribute('data-tab');
      navItems.forEach(n => n.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      item.classList.add('active');
      const pane = document.getElementById(targetTab);
      if (pane) pane.classList.add('active');

      if (titles[targetTab]) {
        heading.textContent = titles[targetTab][0];
        subheading.textContent = titles[targetTab][1];
      }
    });
  });

  // Action links from dashboard stat cards
  document.querySelectorAll('.stat-card').forEach(card => {
    card.addEventListener('click', () => {
      const target = card.getAttribute('data-action');
      const navBtn = document.querySelector(`.nav-item[data-tab="${target}"]`);
      if (navBtn) navBtn.click();
    });
  });
}

// Global master state
let currentProductionBundle = null;

// Dashboard / Full Pipeline Automation
function initDashboard() {
  const quickTopicInput = document.getElementById('quick-topic-input');
  const btnLaunchAuto = document.getElementById('btn-launch-full-auto');
  const btnQuickRun = document.getElementById('btn-quick-run-pipeline');
  const masterCard = document.getElementById('master-output-card');
  const btnExportFull = document.getElementById('btn-export-full-bundle');

  async function runFullPipeline() {
    const topic = quickTopicInput.value.trim() || 'How to Build Autonomous AI Agents in 2026';
    btnLaunchAuto.textContent = '⏳ Engineering Complete Bundle...';
    btnLaunchAuto.disabled = true;

    try {
      // 1. Generate & score hooks
      const hookRes = await fetch('/api/hook/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
      }).then(r => r.json());

      const bestHook = hookRes.best_hook || hookRes.hooks[0];

      // 2. Generate full script
      const scriptRes = await fetch('/api/script/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          target_duration_minutes: 8,
          selected_hook: bestHook.hook
        })
      }).then(r => r.json());

      // 3. Generate packages
      const pkgRes = await fetch('/api/package/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
      }).then(r => r.json());

      const bestPkg = pkgRes.packages[0];

      // 4. Generate SEO
      const chaptersText = "0:00 Introduction & Hook\n0:45 The Foundation & Core Mistake\n2:30 Step-by-Step Playbook\n5:00 The Payoff & Live Proof\n7:00 Next Steps & Resources";
      const seoRes = await fetch('/api/seo/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: bestPkg.title,
          topic,
          chapters: chaptersText
        })
      }).then(r => r.json());

      currentProductionBundle = {
        topic,
        bestHook,
        scriptRes,
        bestPkg,
        seoRes,
        generatedAt: new Date().toISOString()
      };

      renderMasterBundle(currentProductionBundle);
      masterCard.style.display = 'block';
      masterCard.scrollIntoView({ behavior: 'smooth' });
      showToast('Complete Production Bundle generated!');
    } catch (err) {
      console.error(err);
      showToast('Error generating bundle: ' + err.message, 'error');
    } finally {
      btnLaunchAuto.textContent = '⚡ Generate Complete Package';
      btnLaunchAuto.disabled = false;
    }
  }

  btnLaunchAuto.addEventListener('click', runFullPipeline);
  btnQuickRun.addEventListener('click', runFullPipeline);

  // Subtabs in master output card
  document.querySelectorAll('.subtab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.subtab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.subtab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const target = btn.getAttribute('data-sub');
      const content = document.getElementById(target);
      if (content) content.classList.add('active');
    });
  });

  // Copy & Download Bundle
  document.getElementById('btn-copy-master-bundle').addEventListener('click', () => {
    if (!currentProductionBundle) return;
    const md = formatBundleToMarkdown(currentProductionBundle);
    navigator.clipboard.writeText(md);
    showToast('Copied full video production bundle in Markdown!');
  });

  document.getElementById('btn-download-master-bundle').addEventListener('click', () => {
    if (!currentProductionBundle) return;
    const md = formatBundleToMarkdown(currentProductionBundle);
    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `youtube-bundle-${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Downloaded production bundle!');
  });

  btnExportFull.addEventListener('click', () => {
    if (!currentProductionBundle) {
      runFullPipeline();
    } else {
      document.getElementById('btn-copy-master-bundle').click();
    }
  });

  // AI Video Render Button
  const btnRenderVideo = document.getElementById('btn-render-master-video');
  btnRenderVideo.addEventListener('click', async () => {
    if (!currentProductionBundle || !currentProductionBundle.scriptRes) {
      showToast('Generate a production bundle first', 'error');
      return;
    }

    const voice = document.getElementById('master-voice-select').value;
    btnRenderVideo.disabled = true;
    btnRenderVideo.textContent = '⏳ Rendering Voiceover & Video (.mp4)...';

    try {
      const res = await fetch('/api/video/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: currentProductionBundle.bestPkg.title,
          beats: currentProductionBundle.scriptRes.beats,
          voice_key: voice
        })
      }).then(r => r.json());

      const player = document.getElementById('master-video-player');
      const container = document.getElementById('rendered-video-container');
      const durBadge = document.getElementById('video-dur-badge');
      const downloadBtn = document.getElementById('btn-download-mp4');

      player.src = res.video_url;
      durBadge.textContent = `Duration: ${res.duration_seconds}s`;
      downloadBtn.href = res.video_url;
      downloadBtn.setAttribute('download', res.video_filename);

      container.style.display = 'block';
      container.scrollIntoView({ behavior: 'smooth' });
      showToast(`🎬 AI Video Render Complete! (${res.duration_seconds}s MP4)`);
    } catch (err) {
      showToast('Error rendering video: ' + err.message, 'error');
    } finally {
      btnRenderVideo.disabled = false;
      btnRenderVideo.textContent = '🎬 Render AI Video (.mp4)';
    }
  });

  // Direct YouTube Upload Button
  const btnUploadYoutube = document.getElementById('btn-upload-master-youtube');
  btnUploadYoutube.addEventListener('click', async () => {
    if (!currentProductionBundle) {
      showToast('Generate a video bundle first', 'error');
      return;
    }

    const privacy = document.getElementById('master-privacy-select').value;
    btnUploadYoutube.disabled = true;
    btnUploadYoutube.textContent = '🚀 Uploading to YouTube...';

    try {
      const res = await fetch('/api/youtube/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: currentProductionBundle.bestPkg.title,
          description: currentProductionBundle.seoRes.description,
          tags: currentProductionBundle.seoRes.tags,
          privacy_status: privacy
        })
      }).then(r => r.json());

      const statusBox = document.getElementById('youtube-upload-status-box');
      if (res.status === 'uploaded') {
        statusBox.innerHTML = `
          <div class="youtube-upload-card">
            <h4 style="color: var(--yt-green); margin-bottom: 6px;">✅ Successfully Uploaded to YouTube!</h4>
            <p><strong>Title:</strong> ${res.title}</p>
            <p><strong>Privacy Status:</strong> ${res.privacy_status.toUpperCase()}</p>
            <div style="display: flex; gap: 10px; margin-top: 10px;">
              <a href="${res.watch_url}" target="_blank" class="btn btn-sm btn-primary">Watch on YouTube</a>
              <a href="${res.studio_edit_url}" target="_blank" class="btn btn-sm btn-outline">Edit in YouTube Studio</a>
            </div>
          </div>
        `;
        showToast('Video uploaded to YouTube successfully!');
      } else {
        statusBox.innerHTML = `
          <div class="youtube-upload-card ready_for_credentials">
            <h4 style="color: var(--yt-yellow); margin-bottom: 6px;">🔑 1-Step Google Authorization Required</h4>
            <p>Your <code>client_secret.json</code> is ready! Click the link below to grant upload permissions for your channel:</p>
            <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 10px;">
              <a href="#" target="_blank" class="btn btn-primary" id="link-google-oauth" style="display: inline-flex; align-items: center; justify-content: center;">
                👉 1. Click here to Sign in with Google (Opens in new tab)
              </a>
              <div style="display: flex; gap: 8px; margin-top: 6px;">
                <input type="text" id="input-oauth-code" placeholder="2. Paste the redirected URL (or code) here..." style="flex: 1;">
                <button class="btn btn-red" id="btn-submit-oauth-code">Complete Connection</button>
              </div>
            </div>
          </div>
        `;

        // Load auth URL
        fetch('/api/youtube/auth-url')
          .then(r => r.json())
          .then(data => {
            const link = document.getElementById('link-google-oauth');
            if (link && data.auth_url) {
              link.href = data.auth_url;
            }
          });

        // Submit code
        document.getElementById('btn-submit-oauth-code')?.addEventListener('click', async () => {
          const codeInput = document.getElementById('input-oauth-code');
          const submitBtn = document.getElementById('btn-submit-oauth-code');
          const code = codeInput.value.trim();
          if (!code) {
            showToast('Please paste the code or redirected URL first', 'error');
            return;
          }

          submitBtn.disabled = true;
          submitBtn.textContent = 'Connecting...';

          try {
            const res = await fetch('/api/youtube/exchange-code', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ code })
            }).then(r => r.json());

            if (res.status === 'authenticated') {
              showToast(`Connected to channel: ${res.channel_title}!`, 'success');
              statusBox.innerHTML = `
                <div class="youtube-upload-card">
                  <h4 style="color: var(--yt-green); margin-bottom: 6px;">✅ Connected to Channel: ${res.channel_title}</h4>
                  <p>Authorization successful! You can now click <strong>"🚀 1-Click Upload to YouTube"</strong> to publish directly.</p>
                </div>
              `;
            } else {
              showToast(res.detail || 'Authorization failed', 'error');
            }
          } catch (err) {
            showToast('Error: ' + err.message, 'error');
          } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Complete Connection';
          }
        });

        showToast('Client Secret detected! Click the link to authorize.');
      }
      statusBox.style.display = 'block';
    } catch (err) {
      showToast('Upload error: ' + err.message, 'error');
    } finally {
      btnUploadYoutube.disabled = false;
      btnUploadYoutube.textContent = '🚀 1-Click Upload to YouTube';
    }
  });
}

function renderMasterBundle(bundle) {
  // Hook preview
  const hookEl = document.getElementById('master-hook-preview');
  hookEl.innerHTML = `
    <div style="font-size: 1.05rem; font-weight: 600; margin-bottom: 6px; color: #fff;">"${bundle.bestHook.hook}"</div>
    <div style="display: flex; gap: 8px; align-items: center;">
      <span class="badge badge-green">Score: ${bundle.bestHook.score}/100</span>
      <span class="badge badge-accent">Formula: ${bundle.bestHook.formula}</span>
    </div>
  `;

  // Package preview
  const pkgEl = document.getElementById('master-pkg-preview');
  pkgEl.innerHTML = `
    <div style="font-size: 1.05rem; font-weight: 600; margin-bottom: 6px; color: #fff;">${bundle.bestPkg.title}</div>
    <div style="display: flex; gap: 8px; align-items: center;">
      <span class="badge badge-red">Thumb: "${bundle.bestPkg.thumb}"</span>
      <span class="badge badge-green">Score: ${bundle.bestPkg.score}/100</span>
    </div>
  `;

  // Script beats
  const beatsContainer = document.getElementById('master-script-beats');
  beatsContainer.innerHTML = '';
  bundle.scriptRes.beats.forEach((b, idx) => {
    const card = document.createElement('div');
    card.className = 'script-beat-card';
    const imgUrl = b.image_url || '/renders/images/placeholder.jpg';
    card.innerHTML = `
      <div class="beat-header">
        <span class="beat-title">${b.section}</span>
        <div style="display: flex; gap: 6px; align-items: center;">
          ${b.caption_overlay ? `<span class="badge badge-accent">⚡ Subtitle Cue: "${b.caption_overlay}"</span>` : ''}
          <span class="beat-time">${b.timestamp}</span>
        </div>
      </div>
      <div class="beat-card-layout">
        <div class="beat-image-col">
          <img src="${imgUrl}" alt="AI Scene Image" class="beat-scene-img" id="img-beat-master-${idx}" />
          <button class="btn btn-sm btn-outline btn-regen-master-img" data-idx="${idx}" style="font-size: 0.72rem; padding: 4px 8px;">🔄 Regenerate AI Image</button>
        </div>
        <div class="beat-text-col">
          <div style="font-size: 0.8rem; color: #38bdf8; background: rgba(56, 189, 248, 0.08); padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;">
            🎨 <strong>AI Scene Prompt:</strong> ${b.image_prompt || b.visual}
          </div>
          <div class="beat-spoken">${b.spoken}</div>
          <div class="beat-note">💡 ${b.retention_note}</div>
        </div>
      </div>
    `;

    // Regenerate single beat image button
    card.querySelector('.btn-regen-master-img')?.addEventListener('click', async (e) => {
      const btn = e.currentTarget;
      btn.disabled = true;
      btn.textContent = '⏳ Generating...';
      try {
        const res = await fetch('/api/script/regenerate-image', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: b.image_prompt, beat_index: idx })
        }).then(r => r.json());

        b.image_url = res.image_url;
        const imgEl = document.getElementById(`img-beat-master-${idx}`);
        if (imgEl) imgEl.src = res.image_url + '?t=' + Date.now();
        showToast(`New AI Image generated for ${b.section}!`);
      } catch (err) {
        showToast('Error generating image: ' + err.message, 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = '🔄 Regenerate AI Image';
      }
    });

    beatsContainer.appendChild(card);
  });

  // SEO
  document.getElementById('master-seo-content').textContent = bundle.seoRes.description;

  // EDL preview
  document.getElementById('master-edl-content').innerHTML = `
    <p style="color: var(--yt-text-muted); font-size: 0.9rem; margin-bottom: 12px;">Standard 0.45s Dead-Air floor ready. When video is recorded, paste your .srt transcript in the Edit Decision List tab for exact cut timecodes.</p>
    <div class="cut-row"><span class="cut-badge DEAD">RULE</span> Remove silence gaps > 0.45s</div>
    <div class="cut-row"><span class="cut-badge FILLER">RULE</span> Cut solitary filler cues ("um", "so yeah", "basically")</div>
    <div class="cut-row"><span class="cut-badge REPEAT">RULE</span> Cut restarted takes of the same sentence opening</div>
  `;
}

function formatBundleToMarkdown(bundle) {
  return `# YouTube Production Bundle: ${bundle.topic}

## 1. Title & Packaging
* **Title**: ${bundle.bestPkg.title}
* **Thumbnail Text**: ${bundle.bestPkg.thumb}
* **Packaging Score**: ${bundle.bestPkg.score}/100

## 2. The Hook
* **Spoken Hook**: "${bundle.bestHook.hook}"
* **Formula**: ${bundle.bestHook.formula}
* **Hook Score**: ${bundle.bestHook.score}/100 (${bundle.bestHook.band})

## 3. Spoken Script & Retention Beats (Runtime: ~${bundle.scriptRes.estimated_duration_minutes} mins)
${bundle.scriptRes.beats.map(b => `### ${b.section} (${b.timestamp})
* **Visual**: ${b.visual}
* **Spoken**: ${b.spoken}
* **Retention Note**: ${b.retention_note}
`).join('\n')}

## 4. YouTube Description & SEO
\`\`\`
${bundle.seoRes.description}
\`\`\`

## 5. Target Search Queries
${bundle.seoRes.target_queries.map(q => `* ${q}`).join('\n')}

## 6. Tags
\`${bundle.seoRes.tags_string}\`
`;
}

// 1. Hook & Script Lab
function initHookAndScript() {
  const topicInput = document.getElementById('script-topic');
  const btnSample = document.getElementById('btn-sample-script');
  const btnGenHooks = document.getElementById('btn-generate-hooks');
  const btnGenScript = document.getElementById('btn-generate-full-script');
  const singleHookInput = document.getElementById('single-hook-input');
  const btnScoreSingle = document.getElementById('btn-score-single-hook');
  const hookResultsList = document.getElementById('hook-results-list');
  const fullScriptCard = document.getElementById('full-script-card');
  const scriptBeatsOutput = document.getElementById('script-beats-output');
  const btnCopyScript = document.getElementById('btn-copy-script');

  let currentHooks = [];
  let selectedHookText = null;

  btnSample.addEventListener('click', () => {
    topicInput.value = 'How to Automate Content Creation with Agentic AI';
    showToast('Loaded sample topic');
  });

  async function fetchHooks() {
    const topic = topicInput.value.trim();
    if (!topic) {
      showToast('Please enter a video topic first', 'error');
      return;
    }
    btnGenHooks.disabled = true;
    btnGenHooks.textContent = 'Scoring 5 Formulas...';

    try {
      const data = await fetch('/api/hook/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
      }).then(r => r.json());

      currentHooks = data.hooks || [];
      renderHookResults(currentHooks);
      showToast('Evaluated 5 hook formulas!');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btnGenHooks.disabled = false;
      btnGenHooks.textContent = '1. Generate & Score 5 Hooks';
    }
  }

  btnGenHooks.addEventListener('click', fetchHooks);

  btnScoreSingle.addEventListener('click', async () => {
    const hook = singleHookInput.value.trim();
    if (!hook) return;
    btnScoreSingle.disabled = true;
    try {
      const data = await fetch('/api/hook/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hook })
      }).then(r => r.json());

      renderHookResults([data]);
      showToast(`Hook scored: ${data.score}/100 (${data.band})`);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btnScoreSingle.disabled = false;
    }
  });

  function renderHookResults(hooks) {
    hookResultsList.innerHTML = '';
    hooks.forEach((h, index) => {
      const isTop = index === 0;
      const card = document.createElement('div');
      card.className = `hook-card ${isTop ? 'winning' : ''}`;
      card.innerHTML = `
        <div class="hook-card-header">
          <span class="hook-formula-name">${h.formula || 'Custom Hook'}</span>
          <span class="hook-score-badge ${h.band}">${h.score}/100 ${h.band}</span>
        </div>
        <div class="hook-text">"${h.hook}"</div>
        <div class="hook-props-grid">
          <div class="hook-prop-item"><span class="hook-prop-label">Specific</span><span class="hook-prop-val">${h.properties?.SPECIFICITY || 0}</span></div>
          <div class="hook-prop-item"><span class="hook-prop-label">Address</span><span class="hook-prop-val">${h.properties?.ADDRESS || 0}</span></div>
          <div class="hook-prop-item"><span class="hook-prop-label">Stakes</span><span class="hook-prop-val">${h.properties?.STAKES || 0}</span></div>
          <div class="hook-prop-item"><span class="hook-prop-label">Curiosity</span><span class="hook-prop-val">${h.properties?.CURIOSITY || 0}</span></div>
          <div class="hook-prop-item"><span class="hook-prop-label">Brevity</span><span class="hook-prop-val">${h.properties?.BREVITY || 0}</span></div>
        </div>
        ${h.fix_tip ? `<div class="hook-fix-tip">💡 Weakest (${h.weakest_property}): ${h.fix_tip}</div>` : ''}
        <button class="btn btn-sm btn-outline mt-2 btn-select-this-hook">Select for Script</button>
      `;

      card.querySelector('.btn-select-this-hook').addEventListener('click', () => {
        selectedHookText = h.hook;
        document.querySelectorAll('.hook-card').forEach(c => c.classList.remove('winning'));
        card.classList.add('winning');
        showToast('Selected hook for full script!');
      });

      hookResultsList.appendChild(card);
    });
  }

  btnGenScript.addEventListener('click', async () => {
    const topic = topicInput.value.trim();
    if (!topic) {
      showToast('Enter topic first', 'error');
      return;
    }
    btnGenScript.disabled = true;
    btnGenScript.textContent = 'Generating Script...';

    try {
      const dur = parseInt(document.getElementById('script-duration').value, 10);
      const cta = document.getElementById('script-cta').value.trim();
      const res = await fetch('/api/script/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          target_duration_minutes: dur,
          call_to_action: cta,
          selected_hook: selectedHookText
        })
      }).then(r => r.json());

      // Render beats with AI Scene Images
      scriptBeatsOutput.innerHTML = '';
      res.beats.forEach((b, idx) => {
        const beatCard = document.createElement('div');
        beatCard.className = 'script-beat-card';
        const imgUrl = b.image_url || '/renders/images/placeholder.jpg';
        beatCard.innerHTML = `
          <div class="beat-header">
            <span class="beat-title">${b.section}</span>
            <div style="display: flex; gap: 6px; align-items: center;">
              ${b.caption_overlay ? `<span class="badge badge-accent">⚡ Subtitle Cue: "${b.caption_overlay}"</span>` : ''}
              <span class="beat-time">${b.timestamp}</span>
            </div>
          </div>
          <div class="beat-card-layout">
            <div class="beat-image-col">
              <img src="${imgUrl}" alt="AI Scene Image" class="beat-scene-img" id="img-beat-lab-${idx}" />
              <button class="btn btn-sm btn-outline btn-regen-lab-img" data-idx="${idx}" style="font-size: 0.72rem; padding: 4px 8px;">🔄 Regenerate AI Image</button>
            </div>
            <div class="beat-text-col">
              <div style="font-size: 0.8rem; color: #38bdf8; background: rgba(56, 189, 248, 0.08); padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;">
                🎨 <strong>AI Scene Prompt:</strong> ${b.image_prompt || b.visual}
              </div>
              <div class="beat-spoken">${b.spoken}</div>
              <div class="beat-note">💡 ${b.retention_note}</div>
            </div>
          </div>
        `;

        // Regenerate single beat image button
        beatCard.querySelector('.btn-regen-lab-img')?.addEventListener('click', async (e) => {
          const btn = e.currentTarget;
          btn.disabled = true;
          btn.textContent = '⏳ Generating...';
          try {
            const regenRes = await fetch('/api/script/regenerate-image', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ prompt: b.image_prompt || b.visual, beat_index: idx })
            }).then(r => r.json());

            b.image_url = regenRes.image_url;
            const imgEl = document.getElementById(`img-beat-lab-${idx}`);
            if (imgEl) imgEl.src = regenRes.image_url + '?t=' + Date.now();
            showToast(`New AI Image generated for ${b.section}!`);
          } catch (err) {
            showToast('Error generating image: ' + err.message, 'error');
          } finally {
            btn.disabled = false;
            btn.textContent = '🔄 Regenerate AI Image';
          }
        });

        scriptBeatsOutput.appendChild(beatCard);
      });

      document.getElementById('script-meta-pills').innerHTML = `
        <span class="badge badge-green">Est: ${res.estimated_duration_minutes} Mins</span>
        <span class="badge badge-accent">${res.total_words} Words @ 150 WPM</span>
      `;

      fullScriptCard.style.display = 'block';
      fullScriptCard.scrollIntoView({ behavior: 'smooth' });
      showToast('Full script generated!');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btnGenScript.disabled = false;
      btnGenScript.textContent = '2. Generate Full Script';
    }
  });

  btnCopyScript.addEventListener('click', () => {
    const text = Array.from(document.querySelectorAll('.script-beat-card')).map(card => {
      const title = card.querySelector('.beat-title').innerText;
      const visual = card.querySelector('.beat-visual').innerText;
      const spoken = card.querySelector('.beat-spoken').innerText;
      return `${title}\n${visual}\n${spoken}\n`;
    }).join('\n---\n');

    navigator.clipboard.writeText(text);
    showToast('Copied script to clipboard!');
  });
}

// 2. Packaging Studio & Linter
function initPackagingLinter() {
  const titleInput = document.getElementById('pkg-title');
  const thumbInput = document.getElementById('pkg-thumb');
  const charCount = document.getElementById('pkg-title-char-count');
  const meterFill = document.getElementById('pkg-title-meter-fill');
  const btnLint = document.getElementById('btn-lint-package');
  const btnSuggest = document.getElementById('btn-generate-package-ideas');
  const btnSample = document.getElementById('btn-sample-package');

  // Previews
  const previewDesktopTitle = document.getElementById('preview-desktop-title');
  const previewThumbText = document.getElementById('preview-thumb-text');
  const previewMobileTitle = document.getElementById('preview-mobile-title');
  const previewMobileThumbText = document.getElementById('preview-mobile-thumb-text');

  btnSample.addEventListener('click', () => {
    titleInput.value = 'Why 90% of AI Agents Fail (And How to Fix It)';
    thumbInput.value = 'THE 1 FIX';
    updateLivePreviews();
    btnLint.click();
  });

  function updateLivePreviews() {
    const title = titleInput.value.trim() || 'Your Video Title Goes Here';
    const thumb = thumbInput.value.trim() || 'THUMB TEXT';

    charCount.textContent = title.length;
    const pct = Math.min(100, (title.length / 60) * 100);
    meterFill.style.width = pct + '%';
    meterFill.style.background = title.length > 60 ? '#f87171' : title.length > 40 ? '#fbbf24' : '#34d399';

    previewDesktopTitle.textContent = title.length > 60 ? title.substring(0, 60) + '...' : title;
    previewMobileTitle.textContent = title.length > 40 ? title.substring(0, 40) + '...' : title;
    previewThumbText.textContent = thumb;
    previewMobileThumbText.textContent = thumb;
  }

  titleInput.addEventListener('input', updateLivePreviews);
  thumbInput.addEventListener('input', updateLivePreviews);

  btnLint.addEventListener('click', async () => {
    const title = titleInput.value.trim();
    const thumb = thumbInput.value.trim();
    if (!title) {
      showToast('Enter a title to lint', 'error');
      return;
    }

    try {
      const res = await fetch('/api/package/lint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, thumbnail_text: thumb })
      }).then(r => r.json());

      const resultsBox = document.getElementById('linter-results-box');
      const scoreBadge = document.getElementById('pkg-score-badge');
      const statusH = document.getElementById('pkg-score-status');
      const issuesList = document.getElementById('pkg-issues-list');
      const goodList = document.getElementById('pkg-good-list');

      scoreBadge.textContent = `${res.score}/100`;
      scoreBadge.style.color = res.score >= 75 ? 'var(--yt-green)' : res.score >= 50 ? 'var(--yt-yellow)' : '#f87171';
      statusH.textContent = res.score >= 75 ? 'Strong Packaging' : res.score >= 50 ? 'Needs Refinement' : 'Severe Weaknesses';

      issuesList.innerHTML = res.issues.map(i => `<div class="issue-row"><span>❌</span> <strong>${i.category}:</strong> ${i.message}</div>`).join('');
      goodList.innerHTML = res.good.map(g => `<div class="good-row"><span>✅</span> ${g}</div>`).join('');

      resultsBox.style.display = 'block';
      showToast(`Packaging Score: ${res.score}/100`);
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  btnSuggest.addEventListener('click', async () => {
    const topic = titleInput.value.trim() || 'AI Automation';
    try {
      const res = await fetch('/api/package/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
      }).then(r => r.json());

      const container = document.getElementById('suggested-packages-container');
      const list = document.getElementById('suggested-packages-list');
      list.innerHTML = res.packages.map(p => `
        <div class="hook-card" style="margin-bottom: 8px; cursor: pointer;">
          <div style="display: flex; justify-content: space-between; font-weight: 600;">
            <span>${p.title}</span>
            <span class="badge badge-green">${p.score}/100</span>
          </div>
          <div style="color: var(--yt-red); font-size: 0.8rem; margin-top: 4px;">Thumbnail: "${p.thumb}"</div>
        </div>
      `).join('');

      container.style.display = 'block';
      list.querySelectorAll('.hook-card').forEach((card, idx) => {
        card.addEventListener('click', () => {
          const item = res.packages[idx];
          titleInput.value = item.title;
          thumbInput.value = item.thumb;
          updateLivePreviews();
          btnLint.click();
        });
      });
      showToast('Generated 5 high-scoring title pairs');
    } catch (err) {
      showToast(err.message, 'error');
    }
  });
}

// 3. Edit Decision List (EDL)
function initEditDecisionList() {
  const transcriptInput = document.getElementById('edl-transcript');
  const floorInput = document.getElementById('edl-floor');
  const btnProcess = document.getElementById('btn-process-edl');
  const btnSample = document.getElementById('btn-sample-transcript');
  const statsGrid = document.getElementById('edl-stats-grid');
  const cutsList = document.getElementById('edl-cuts-list');
  const btnCopyEdl = document.getElementById('btn-copy-edl');

  const sampleSRT = `1
00:00:00,000 --> 00:00:03,500
If you are still building AI agents the manual way in 2026

2
00:00:03,500 --> 00:00:04,800
um like basically

3
00:00:05,800 --> 00:00:08,200
you are wasting 3 hours every week.

4
00:00:08,200 --> 00:00:10,000
In this video we are going to

5
00:00:10,000 --> 00:00:11,200
um yeah

6
00:00:12,000 --> 00:00:15,000
In this video we are going to build an end to end pipeline.`;

  btnSample.addEventListener('click', () => {
    transcriptInput.value = sampleSRT;
    showToast('Loaded sample transcript with dead air & filler');
  });

  let currentCuts = [];

  btnProcess.addEventListener('click', async () => {
    const text = transcriptInput.value.trim();
    if (!text) {
      showToast('Paste a timestamped transcript first', 'error');
      return;
    }
    const floor = parseFloat(floorInput.value) || 0.45;

    try {
      const res = await fetch('/api/edit/deadair', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript_text: text, floor })
      }).then(r => r.json());

      currentCuts = res.cuts;
      document.getElementById('edl-stat-original').textContent = `${res.duration}s`;
      document.getElementById('edl-stat-removed').textContent = `-${res.removed_seconds}s`;
      document.getElementById('edl-stat-final').textContent = `${res.final_duration}s`;
      document.getElementById('edl-stat-pct').textContent = `${res.time_saved_percent}%`;
      statsGrid.style.display = 'grid';

      cutsList.innerHTML = res.cuts.map(c => `
        <div class="cut-row">
          <span class="cut-badge ${c.kind}">${c.kind}</span>
          <span><strong>${c.start}s -> ${c.end}s</strong> (${(c.end - c.start).toFixed(2)}s)</span>
          <span style="color: var(--yt-text-muted); margin-left: auto;">${c.why}</span>
        </div>
      `).join('');

      showToast(`Processed ${res.cuts_count} cuts! Saved ${res.time_saved_percent}% runtime.`);
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  btnCopyEdl.addEventListener('click', () => {
    if (!currentCuts.length) return;
    const txt = currentCuts.map(c => `[${c.kind}] ${c.start}s - ${c.end}s (${c.why})`).join('\n');
    navigator.clipboard.writeText(txt);
    showToast('Copied Edit Decision List!');
  });
}

// 4. Chapters Builder
function initChaptersBuilder() {
  const transcriptInput = document.getElementById('chapters-transcript');
  const targetCountInput = document.getElementById('chapters-target-count');
  const btnGenerate = document.getElementById('btn-generate-chapters');
  const btnSample = document.getElementById('btn-sample-chapters-transcript');
  const outputBox = document.getElementById('chapters-output-box');
  const btnCopy = document.getElementById('btn-copy-chapters');

  btnSample.addEventListener('click', () => {
    transcriptInput.value = `1
00:00:00,000 --> 00:00:15,000
Welcome back today we are breaking down autonomous YouTube skill engineering.

2
00:00:16,000 --> 00:00:45,000
First let us establish the fundamental principles of hook formulas and script retention.

3
00:00:46,000 --> 00:01:30,000
Now moving into packaging title and thumbnail linters to maximize click through rate.

4
00:01:31,000 --> 00:02:15,000
Next we will look at dead air extraction and edit decision lists for transcripts.

5
00:02:16,000 --> 00:03:00,000
Finally we will cover audience retention curves cliff detection and weekly plans.`;
    showToast('Loaded sample transcript');
  });

  btnGenerate.addEventListener('click', async () => {
    const text = transcriptInput.value.trim();
    if (!text) {
      showToast('Paste a transcript first', 'error');
      return;
    }
    const target = parseInt(targetCountInput.value, 10) || 7;

    try {
      const res = await fetch('/api/chapters/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript_text: text, target_chapters: target })
      }).then(r => r.json());

      outputBox.value = res.formatted_text;
      showToast(`Generated ${res.total_chapters} YouTube-validated chapters!`);
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  btnCopy.addEventListener('click', () => {
    if (!outputBox.value) return;
    navigator.clipboard.writeText(outputBox.value);
    showToast('Copied chapters to clipboard!');
  });
}

// 5. Shorts Extractor
function initShortsExtractor() {
  const transcriptInput = document.getElementById('shorts-transcript');
  const btnExtract = document.getElementById('btn-extract-shorts');
  const btnSample = document.getElementById('btn-sample-shorts-transcript');
  const resultsGrid = document.getElementById('shorts-results-grid');

  btnSample.addEventListener('click', () => {
    transcriptInput.value = `1
00:00:00,000 --> 00:00:40,000
The number one mistake creators make is spending 10 hours editing a video with a hook that leaks 50% in the first 15 seconds. If the viewer is gone in the first 15 seconds, the rest of the video does not exist.

2
00:00:41,000 --> 00:01:25,000
When you look at YouTube packaging, the title and thumbnail are a single unit. A title that repeats what the thumbnail already says wastes 50% of your click surface.`;
    showToast('Loaded long-form transcript');
  });

  btnExtract.addEventListener('click', async () => {
    const text = transcriptInput.value.trim();
    if (!text) {
      showToast('Enter transcript first', 'error');
      return;
    }
    try {
      const res = await fetch('/api/shorts/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript_text: text, max_shorts: 3 })
      }).then(r => r.json());

      resultsGrid.innerHTML = res.shorts.map(s => `
        <div class="short-clip-card">
          <h4>📱 Short #${s.short_id} (${s.timecode})</h4>
          <p style="font-weight: 600; color: #fff; margin-bottom: 6px;">"${s.generated_hook}"</p>
          <p style="font-size: 0.8rem; color: var(--yt-text-muted); margin-bottom: 8px;">Quote: ${s.core_quote}</p>
          <div style="font-size: 0.72rem; color: var(--yt-accent); background: var(--yt-bg-main); padding: 6px; border-radius: 4px;">🎬 ${s.edit_direction}</div>
        </div>
      `).join('');

      showToast(`Extracted ${res.total_extracted} high-impact Shorts!`);
    } catch (err) {
      showToast(err.message, 'error');
    }
  });
}

// 6. SEO & Metadata
function initSeoGenerator() {
  const titleInput = document.getElementById('seo-title');
  const topicInput = document.getElementById('seo-topic');
  const chaptersInput = document.getElementById('seo-chapters-input');
  const btnGenerate = document.getElementById('btn-generate-seo');
  const btnSample = document.getElementById('btn-sample-seo');
  const descOutput = document.getElementById('seo-description-output');
  const tagsOutput = document.getElementById('seo-tags-output');
  const queriesList = document.getElementById('seo-queries-list');
  const btnCopy = document.getElementById('btn-copy-seo');

  btnSample.addEventListener('click', () => {
    titleInput.value = 'Why 90% of AI Agents Fail (And How to Fix It)';
    topicInput.value = 'Autonomous AI Agent Workflows';
    chaptersInput.value = '0:00 Intro\n1:00 Common Pitfalls\n3:20 Step-by-Step Architecture';
  });

  btnGenerate.addEventListener('click', async () => {
    const title = titleInput.value.trim() || 'AI Agent Workflow Guide';
    const topic = topicInput.value.trim() || 'AI Automation';
    const chapters = chaptersInput.value.trim();

    try {
      const res = await fetch('/api/seo/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, topic, chapters })
      }).then(r => r.json());

      descOutput.value = res.description;
      tagsOutput.value = res.tags_string;
      queriesList.innerHTML = res.target_queries.map(q => `<li>🔍 ${q}</li>`).join('');
      showToast('SEO package generated!');
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  btnCopy.addEventListener('click', () => {
    if (!descOutput.value) return;
    navigator.clipboard.writeText(descOutput.value);
    showToast('Copied description to clipboard!');
  });
}

// 7. Retention Radar
function initRetentionRadar() {
  const csvInput = document.getElementById('retention-csv-input');
  const btnSample = document.getElementById('btn-sample-retention');
  const btnAnalyze = document.getElementById('btn-analyze-retention');
  const metricsBox = document.getElementById('retention-metrics-container');
  const chartBox = document.getElementById('retention-chart-box');
  const svgWrapper = document.getElementById('retention-svg-wrapper');
  const cliffsList = document.getElementById('retention-cliffs-list');

  const sampleCSV = `Position,Percent
0,100
5,88
10,79
15,73
25,68
30,64
60,58
90,52
120,41
150,39
180,36
240,32
300,28`;

  btnSample.addEventListener('click', () => {
    csvInput.value = sampleCSV;
    showToast('Loaded sample retention curve');
  });

  btnAnalyze.addEventListener('click', async () => {
    const csvData = csvInput.value.trim();
    if (!csvData) {
      showToast('Paste CSV data first', 'error');
      return;
    }

    try {
      const res = await fetch('/api/retention/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ csv_data: csvData })
      }).then(r => r.json());

      document.getElementById('r-hook-leak').textContent = `${res.hook_leak_pct}%`;
      const badge = document.getElementById('r-hook-badge');
      badge.textContent = res.hook_verdict.toUpperCase();
      badge.className = `r-badge ${res.hook_verdict === 'healthy' ? 'badge-green' : 'badge-red'}`;

      document.getElementById('r-cliffs-count').textContent = res.cliffs.length;
      document.getElementById('r-slide-rate').textContent = `${res.slide_rate}%/s`;

      metricsBox.style.display = 'flex';
      chartBox.style.display = 'block';

      renderRetentionChart(res.curve_data, res.cliffs);

      cliffsList.innerHTML = '<h4>⚠️ Detected Cliff Drops:</h4>' +
        (res.cliffs.length ? res.cliffs.map(c => `
          <div class="cut-row">
            <span class="cut-badge DEAD">-${c.lost}%</span>
            <span>Drop between <strong>${c.from}s and ${c.to}s</strong></span>
          </div>
        `).join('') : '<p style="color:var(--yt-text-muted);font-size:0.85rem;">No abrupt cliff drops detected. Audience loss is gradual slide.</p>');

      showToast(`Analyzed retention curve: ${res.hook_leak_pct}% lost in opening.`);
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  function renderRetentionChart(curve, cliffs) {
    const width = 600;
    const height = 200;
    const padding = 30;

    const maxX = Math.max(...curve.map(p => p.x), 100);
    const maxY = 100;

    const points = curve.map(p => {
      const x = padding + (p.x / maxX) * (width - 2 * padding);
      const y = height - padding - (p.y / maxY) * (height - 2 * padding);
      return `${x},${y}`;
    }).join(' ');

    const svg = `
      <svg viewBox="0 0 ${width} ${height}" style="width:100%;height:auto;overflow:visible;">
        <defs>
          <linearGradient id="curveGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#ff0033" stop-opacity="0.4"/>
            <stop offset="100%" stop-color="#ff0033" stop-opacity="0.0"/>
          </linearGradient>
        </defs>
        <!-- Grid lines -->
        <line x1="${padding}" y1="${padding}" x2="${width-padding}" y2="${padding}" stroke="#262e3d" stroke-dasharray="4"/>
        <line x1="${padding}" y1="${height/2}" x2="${width-padding}" y2="${height/2}" stroke="#262e3d" stroke-dasharray="4"/>
        <line x1="${padding}" y1="${height-padding}" x2="${width-padding}" y2="${height-padding}" stroke="#343e52"/>
        
        <!-- Y Axis Labels -->
        <text x="5" y="${padding+4}" fill="#6b7280" font-size="10">100%</text>
        <text x="12" y="${height/2+4}" fill="#6b7280" font-size="10">50%</text>
        <text x="18" y="${height-padding+4}" fill="#6b7280" font-size="10">0%</text>
        
        <!-- Curve -->
        <polyline fill="none" stroke="#ff0033" stroke-width="3" points="${points}"/>
      </svg>
    `;
    svgWrapper.innerHTML = svg;
  }
}

// 8. Viral Outlier Radar
function initViralOutliers() {
  const jsonInput = document.getElementById('viral-json-input');
  const minMultInput = document.getElementById('viral-min-mult');
  const btnAnalyze = document.getElementById('btn-analyze-viral');
  const btnSample = document.getElementById('btn-sample-viral');
  const tableContainer = document.getElementById('viral-outliers-table-container');
  const tbody = document.getElementById('viral-outliers-tbody');

  const sampleViralData = [
    {"channel": "AI Builders", "title": "Why 90% of AI Startups Fail in 2026", "views": 420000},
    {"channel": "AI Builders", "title": "My Weekly Coding Setup", "views": 32000},
    {"channel": "AI Builders", "title": "Top 5 VS Code Extensions", "views": 28000},
    {"channel": "AI Builders", "title": "How to Learn Python Fast", "views": 35000},
    {"channel": "Tech Lead Pro", "title": "Stop Doing AI Automation Like This", "views": 680000},
    {"channel": "Tech Lead Pro", "title": "Office Tour 2026", "views": 45000},
    {"channel": "Tech Lead Pro", "title": "Q&A Session #12", "views": 38000},
    {"channel": "Tech Lead Pro", "title": "Code Review #4", "views": 42000}
  ];

  btnSample.addEventListener('click', () => {
    jsonInput.value = JSON.stringify(sampleViralData, null, 2);
    showToast('Loaded sample niche channel dataset');
  });

  btnAnalyze.addEventListener('click', async () => {
    let videos = [];
    try {
      videos = JSON.parse(jsonInput.value.trim());
    } catch (e) {
      showToast('Invalid JSON format', 'error');
      return;
    }
    const minMult = parseFloat(minMultInput.value) || 1.5;

    try {
      const res = await fetch('/api/viral/swipe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ videos, min_multiplier: minMult })
      }).then(r => r.json());

      tbody.innerHTML = res.outliers.map(o => `
        <tr>
          <td><span class="badge badge-red" style="font-size:0.85rem;">${o.multiple}x</span></td>
          <td><strong>${o.views.toLocaleString()}</strong></td>
          <td style="color:var(--yt-text-muted);">${o.median.toLocaleString()}</td>
          <td>${o.channel}</td>
          <td style="font-weight:600; color:#fff;">${o.title}</td>
          <td><span class="badge badge-accent">${o.formula}</span></td>
        </tr>
      `).join('');

      tableContainer.style.display = 'block';
      showToast(`Found ${res.outliers.length} breakout outliers!`);
    } catch (err) {
      showToast(err.message, 'error');
    }
  });
}

// 9. Comment Manager
function initCommentManager() {
  const input = document.getElementById('comments-input');
  const btnSample = document.getElementById('btn-sample-comments');
  const btnTriage = document.getElementById('btn-triage-comments');
  const outputGrid = document.getElementById('comments-triage-output');

  btnSample.addEventListener('click', () => {
    input.value = `Alex: This video saved me 10 hours this week! Absolute gold!
Sarah: How do I connect the Python EDL script to Premiere Pro?
Dave: I disagree with step 3, manual editing is still faster for small cuts.
Mark: Great video man, subscribed!`;
    showToast('Loaded sample comments');
  });

  btnTriage.addEventListener('click', async () => {
    const raw = input.value.trim();
    if (!raw) return;

    let commentList = [];
    if (raw.startsWith('[')) {
      try { commentList = JSON.parse(raw); } catch (e) {}
    }
    if (!commentList.length) {
      commentList = raw.split('\n').filter(l => l.trim()).map(l => {
        const parts = l.split(':');
        return { author: parts[0].trim(), text: parts.slice(1).join(':').trim() || l.trim() };
      });
    }

    try {
      const res = await fetch('/api/comments/triage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comments: commentList })
      }).then(r => r.json());

      document.getElementById('count-superfans').textContent = res.summary.superfans;
      document.getElementById('count-questions').textContent = res.summary.questions;
      document.getElementById('count-critiques').textContent = res.summary.critiques;
      document.getElementById('count-noise').textContent = res.summary.noise;

      const renderPile = (pileId, items) => {
        const container = document.getElementById(pileId);
        container.innerHTML = items.map(i => `
          <div class="hook-card" style="margin-bottom:8px;">
            <div style="font-weight:600; color:#fff; font-size:0.85rem;">${i.author}: "${i.comment}"</div>
            <div style="font-size:0.75rem; color:var(--yt-accent); margin-top:4px;">💬 Reply: ${i.suggested_reply}</div>
          </div>
        `).join('');
      };

      renderPile('pile-superfans', res.piles.superfans);
      renderPile('pile-questions', res.piles.questions);
      renderPile('pile-critiques', res.piles.critiques);
      renderPile('pile-noise', res.piles.noise);

      outputGrid.style.display = 'grid';
      showToast(`Triaged ${res.summary.total} comments into 4 piles!`);
    } catch (err) {
      showToast(err.message, 'error');
    }
  });
}

// 10. Channel Audit & Weekly Plan
function initChannelAuditAndPlan() {
  const btnAudit = document.getElementById('btn-run-audit');
  const btnPlan = document.getElementById('btn-generate-plan');

  btnAudit.addEventListener('click', async () => {
    const payload = {
      channel_name: document.getElementById('audit-name').value,
      subscribers: parseInt(document.getElementById('audit-subs').value, 10),
      avg_views_last_10: parseInt(document.getElementById('audit-avg-views').value, 10),
      top_video_views: parseInt(document.getElementById('audit-top-views').value, 10),
      upload_frequency_per_week: parseFloat(document.getElementById('audit-freq').value)
    };

    try {
      const res = await fetch('/api/audit/channel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).then(r => r.json());

      const box = document.getElementById('audit-result-box');
      document.getElementById('audit-bottleneck-title').textContent = `🎯 Single Bottleneck: ${res.single_critical_fix.bottleneck}`;
      document.getElementById('audit-prescription-text').textContent = res.single_critical_fix.prescription;
      box.style.display = 'block';
      showToast('Identified single leverage fix!');
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  btnPlan.addEventListener('click', async () => {
    const hours = parseInt(document.getElementById('plan-hours').value, 10);
    const niche = document.getElementById('plan-niche').value;

    try {
      const res = await fetch('/api/plan/weekly', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hours_available: hours, niche })
      }).then(r => r.json());

      const box = document.getElementById('plan-output-box');
      document.getElementById('plan-tier-title').textContent = `📅 ${res.tier} (${res.total_hours}h total)`;

      const list = document.getElementById('plan-deliverables-list');
      list.innerHTML = res.deliverables.map(d => `
        <div class="hook-card" style="margin-bottom: 8px;">
          <div style="display:flex; justify-content:space-between;">
            <strong style="color: #fff;">${d.type}</strong>
            <span class="badge badge-accent">${d.hours_allocated}h</span>
          </div>
          <div style="font-size:0.8rem; color:var(--yt-text-muted); margin-top:4px;">${d.strategy}</div>
          <div style="font-size:0.72rem; color:var(--yt-yellow); margin-top:2px;">🗓️ Schedule: ${d.days}</div>
        </div>
      `).join('');

      box.style.display = 'block';
      showToast('Generated hours-matched weekly schedule!');
    } catch (err) {
      showToast(err.message, 'error');
    }
  });
}

// 11. Voice Profile
function initVoiceProfile() {
  const editor = document.getElementById('voice-editor');
  const btnSave = document.getElementById('btn-save-voice');

  fetch('/api/voice')
    .then(r => r.json())
    .then(data => {
      if (data && data.content) {
        editor.value = data.content;
      }
    });

  btnSave.addEventListener('click', async () => {
    const content = editor.value;
    try {
      await fetch('/api/voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      });
      showToast('Voice Profile (voice.md) updated successfully!');
    } catch (err) {
      showToast(err.message, 'error');
    }
  });
}
