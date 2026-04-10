// ==UserScript==
// @name         哈利波特藏宝阁监控
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  监控哈利波特魔法觉醒藏宝阁，有符合条件的账号时弹出提醒
// @author       you
// @match        https://hp.cbg.163.com/*
// @grant        GM_notification
// @grant        GM_xmlhttpRequest
// @connect      hp.cbg.163.com
// ==/UserScript==

(function () {
  'use strict';

  // ========== 配置区 ==========
  const INTERVAL_SECONDS = 60;  // 每隔多少秒查询一次，建议不要低于30

  const PAYLOAD = new URLSearchParams({
    client_type: 'h5',
    act: 'recommd_by_role',
    search_type: 'role',
    count: '15',
    view_loc: 'search_cond',
    gender__or: '2',
    card_list: JSON.stringify([{ card_list__id: '1198', card_list__level: 15 }]),
    'wand__and': '10000020',
    'rare_cloth__and': '10453621,10453821,10454011,10454025,10454059,10454122',
    'frame__or': '4101162',
    order_by: '',
    page: '1',
    exter: 'cbg.163.com',
  }).toString();
  // ============================

  let timer = null;
  let isRunning = false;

  // 创建悬浮控制面板
  function createPanel() {
    const panel = document.createElement('div');
    panel.id = 'cbg-monitor-panel';
    panel.style.cssText = `
      position: fixed;
      bottom: 80px;
      right: 20px;
      z-index: 99999;
      background: #1a0533;
      color: #f5d87a;
      border-radius: 12px;
      padding: 14px 18px;
      font-size: 13px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.4);
      min-width: 180px;
      user-select: none;
    `;

    panel.innerHTML = `
      <div style="font-weight:bold;margin-bottom:8px;font-size:14px;">🔍 藏宝阁监控</div>
      <div id="cbg-status" style="color:#ccc;margin-bottom:10px;font-size:12px;">状态：未启动</div>
      <div id="cbg-count" style="color:#ccc;margin-bottom:10px;font-size:12px;">查询次数：0</div>
      <button id="cbg-toggle" style="
        width:100%;
        padding:6px 0;
        background:#b8860b;
        color:#fff;
        border:none;
        border-radius:8px;
        cursor:pointer;
        font-size:13px;
        font-weight:bold;
      ">开始监控</button>
    `;

    document.body.appendChild(panel);

    document.getElementById('cbg-toggle').addEventListener('click', toggleMonitor);
  }

  let queryCount = 0;

  function updateStatus(text, color = '#ccc') {
    const el = document.getElementById('cbg-status');
    if (el) {
      el.textContent = '状态：' + text;
      el.style.color = color;
    }
  }

  function updateCount() {
    const el = document.getElementById('cbg-count');
    if (el) el.textContent = '查询次数：' + queryCount;
  }

  function toggleMonitor() {
    const btn = document.getElementById('cbg-toggle');
    if (isRunning) {
      clearInterval(timer);
      isRunning = false;
      btn.textContent = '开始监控';
      updateStatus('已停止', '#ccc');
    } else {
      isRunning = true;
      btn.textContent = '停止监控';
      updateStatus('监控中…', '#f5d87a');
      checkOnce();  // 立即查一次
      timer = setInterval(checkOnce, INTERVAL_SECONDS * 1000);
    }
  }

  function checkOnce() {
    queryCount++;
    updateCount();

    GM_xmlhttpRequest({
      method: 'POST',
      url: 'https://hp.cbg.163.com/cgi-bin/recommend.py?client_type=h5&act=recommd_by_role',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://hp.cbg.163.com/',
        'Origin': 'https://hp.cbg.163.com',
      },
      data: PAYLOAD,
      onload: function (response) {
        try {
          const data = JSON.parse(response.responseText);
          const results = data.result || [];
          if (results.length > 0) {
            onFound(results);
          } else {
            updateStatus('监控中，暂无结果', '#f5d87a');
          }
        } catch (e) {
          updateStatus('解析失败，继续监控', '#e07070');
          console.error('[CBG监控] 解析错误', e);
        }
      },
      onerror: function () {
        updateStatus('请求失败，继续监控', '#e07070');
      }
    });
  }

  function onFound(results) {
    // 停止监控，避免反复弹窗
    clearInterval(timer);
    isRunning = false;
    const btn = document.getElementById('cbg-toggle');
    if (btn) btn.textContent = '开始监控';
    updateStatus(`发现 ${results.length} 个符合账号！`, '#00e676');

    // 浏览器桌面通知
    GM_notification({
      title: '🎉 藏宝阁有符合条件的账号！',
      text: `共找到 ${results.length} 个账号，快去看看！`,
      timeout: 0,  // 不自动关闭
      onclick: function () {
        window.focus();
      }
    });

    // 页面内也弹一个醒目提示
    showAlert(results.length);
  }

  function showAlert(count) {
    const mask = document.createElement('div');
    mask.style.cssText = `
      position: fixed;
      inset: 0;
      z-index: 999999;
      background: rgba(0,0,0,0.6);
      display: flex;
      align-items: center;
      justify-content: center;
    `;

    mask.innerHTML = `
      <div style="
        background:#1a0533;
        border:2px solid #f5d87a;
        border-radius:16px;
        padding:36px 48px;
        text-align:center;
        color:#f5d87a;
        max-width:320px;
      ">
        <div style="font-size:48px;margin-bottom:12px;">🎉</div>
        <div style="font-size:20px;font-weight:bold;margin-bottom:8px;">发现符合条件的账号！</div>
        <div style="font-size:14px;color:#ccc;margin-bottom:24px;">共 ${count} 个账号，点击下方按钮前往查看</div>
        <button id="cbg-goto" style="
          background:#b8860b;color:#fff;border:none;
          border-radius:10px;padding:10px 28px;
          font-size:15px;cursor:pointer;margin-right:10px;
        ">立即查看</button>
        <button id="cbg-close" style="
          background:#444;color:#fff;border:none;
          border-radius:10px;padding:10px 20px;
          font-size:15px;cursor:pointer;
        ">关闭</button>
      </div>
    `;

    document.body.appendChild(mask);

    document.getElementById('cbg-goto').addEventListener('click', () => {
      window.location.href = 'https://hp.cbg.163.com/mweb/?refer_sn=&search_type=role&gender__or=2&card_list=%5B%7B%22card_list__id%22%3A%221198%22%2C%22card_list__level%22%3A15%7D%5D&wand__and=10000020&rare_cloth__and=10453621%2C10453821%2C10454011%2C10454025%2C10454059%2C10454122&frame__or=4101162';
      mask.remove();
    });

    document.getElementById('cbg-close').addEventListener('click', () => {
      mask.remove();
    });
  }

  // 等页面加载完再创建面板
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createPanel);
  } else {
    createPanel();
  }

})();   
