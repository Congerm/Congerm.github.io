/* Data Portal — Observable Plot wrappers + Mermaid ERD + data dictionary. */
var PortalCharts = (function () {
  'use strict';

  var PALETTE = ['#214e63', '#3d7d9c', '#d9a441', '#7ca6b8', '#8f5d2a', '#4a6d7c', '#c9b458', '#5a6b74'];

  function mount(el, plot) {
    el.innerHTML = '';
    el.appendChild(plot);
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function base(opts) {
    return {
      marginLeft: 64,
      width: (opts && opts.width) || 720,
      height: (opts && opts.height) || 360,
      color: opts && opts.stroke ? { legend: true, range: PALETTE } : { range: PALETTE },
      x: { label: (opts && opts.xLabel) || null },
      y: { label: (opts && opts.yLabel) || null, grid: true },
      style: { fontSize: '13px' }
    };
  }

  function lineChart(el, data, opts) {
    opts = opts || {};
    var marks = [Plot.lineY(data, {
      x: opts.x, y: opts.y, stroke: opts.stroke || PALETTE[0],
      curve: 'catmull-rom', tip: true
    })];
    if (opts.ruleY !== false) marks.push(Plot.ruleY([0]));
    mount(el, Plot.plot(Object.assign(base(opts), { marks: marks })));
  }

  function barChart(el, data, opts) {
    opts = opts || {};
    mount(el, Plot.plot(Object.assign(base(opts), {
      marks: [Plot.barY(data, { x: opts.x, y: opts.y, fill: opts.fill || PALETTE[0], tip: true, sort: opts.sort })],
      x: { label: opts.xLabel || null, tickRotate: data.length > 12 ? -45 : 0 }
    })));
  }

  function stackedBar(el, data, opts) {
    opts = opts || {};
    mount(el, Plot.plot(Object.assign(base(opts), {
      marks: [Plot.barY(data, { x: opts.x, y: opts.y, fill: opts.fill, tip: true })],
      x: { label: opts.xLabel || null, tickRotate: (opts.rotateTicks == null ? true : opts.rotateTicks) ? -45 : 0 },
      color: { legend: true, range: PALETTE }
    })));
  }

  /* Plot.rectY + stackY over a temporal x axis (data must hold Date values). */
  function stackedBarTime(el, data, opts) {
    opts = opts || {};
    mount(el, Plot.plot(Object.assign(base(opts), {
      // rectY + interval derives x1/x2 from the date and stacks y implicitly
      marks: [Plot.rectY(data, {
        x: opts.x, interval: opts.interval,
        y: opts.y, fill: opts.fill, tip: true
      })],
      x: { label: opts.xLabel || null },
      color: { legend: true, range: PALETTE }
    })));
  }

  /* Heatmap: x ordinal, y categorical, sequential fill. */
  function cellChart(el, data, opts) {
    opts = opts || {};
    mount(el, Plot.plot({
      width: opts.width || 720,
      height: opts.height || 360,
      x: { label: opts.xLabel || null, tickRotate: -45 },
      y: { label: opts.yLabel || null },
      color: { scheme: 'YlGnBu', legend: true, label: opts.colorLabel || null },
      marks: [Plot.cell(data, {
        x: opts.x, y: opts.y, fill: opts.fill,
        channels: opts.channels, tip: true
      })]
    }));
  }

  /* Grouped bars across an fx facet. */
  function groupedBar(el, data, opts) {
    opts = opts || {};
    var marks = [Plot.barY(data, {
      fx: opts.fx, x: opts.x, y: opts.y,
      fill: opts.fill || PALETTE[0],
      channels: opts.channels, tip: true
    })];
    if (opts.refY != null) marks.push(Plot.ruleY([opts.refY], { stroke: '#999', strokeDasharray: '4 4' }));
    mount(el, Plot.plot(Object.assign(base(opts), {
      fx: { label: opts.fxLabel || null },
      x: { label: opts.xLabel || null, domain: opts.domain },
      marks: marks
    })));
  }

  function scatter(el, data, opts) {
    opts = opts || {};
    var plot = Plot.plot(Object.assign(base(opts), {
      marks: [Plot.dot(data, {
        x: opts.x, y: opts.y,
        fill: opts.fill || PALETTE[0],
        r: opts.r || 3,
        fillOpacity: 0.7,
        title: opts.title,
        tip: true
      })],
      color: opts.fill ? { legend: !!opts.legend, range: PALETTE, type: 'categorical' } : undefined
    }));
    if (opts.onClick) {
      // 'input' fires on hover (tip updates plot.value); only act on real clicks.
      var last = null;
      plot.addEventListener('input', function () { last = plot.value; });
      plot.addEventListener('click', function () {
        var v = Array.isArray(last) ? last[0] : last;
        if (v) opts.onClick(v);
      });
    }
    mount(el, plot);
  }

  function table(el, rows, opts) {
    opts = opts || {};
    if (!rows || !rows.length) {
      el.innerHTML = '<p class="portal-empty">No rows.</p>';
      return;
    }
    var cols = opts.columns || Object.keys(rows[0]);
    var html = '<div class="portal-table-wrap"><table class="portal-table"><thead><tr>' +
      cols.map(function (c) { return '<th>' + esc(c) + '</th>'; }).join('') +
      '</tr></thead><tbody>' +
      rows.map(function (r) {
        return '<tr>' + cols.map(function (c) {
          var v = r[c];
          if (v == null) v = '';
          else if (typeof v === 'object') v = JSON.stringify(v);
          return '<td>' + esc(v) + '</td>';
        }).join('') + '</tr>';
      }).join('') +
      '</tbody></table></div>';
    el.innerHTML = html;
  }

  /* Mermaid UML class diagram restricted to the given schemas (default: all
     schemas in the catalog). Classes are named schema__table; only
     catalog-listed columns appear, with derived columns shown in UML
     derived-attribute form (/name). FK relationships are plain association
     lines with 1..1 / 0..* end labels, drawn when both endpoints survive the
     schema filter. */
  function renderErd(container, catalog, opts) {
    opts = opts || {};
    var schemas = opts.schemas || null;
    var inScope = function (s) { return !schemas || schemas.indexOf(s) !== -1; };

    var tables = (catalog.tables || []).filter(function (t) { return inScope(t.schema); });
    var cols = (catalog.columns || []).filter(function (c) { return inScope(c.schema); });
    var keys = {};
    tables.forEach(function (t) { keys[t.schema + '.' + t.table] = t; });

    function entName(s, t) { return s + '__' + t; }
    function colType(ty) { return String(ty || 'text').toLowerCase().replace(/[^a-z0-9]+/g, '_') || 'text'; }
    function colName(n, access) { return String(n).replace(/[^A-Za-z0-9_]/g, '_'); }

    var byTable = {};
    cols.forEach(function (c) {
      var k = c.schema + '.' + c.table;
      (byTable[k] = byTable[k] || []).push(c);
    });

    var lines = ['classDiagram'];
    tables.forEach(function (t) {
      var k = t.schema + '.' + t.table;
      lines.push('  class ' + entName(t.schema, t.table) + ' {');
      (byTable[k] || [])
        .sort(function (a, b) { return (a.ordinal || 0) - (b.ordinal || 0); })
        .forEach(function (c) {
          var nm = colName(c.column, c.access);
          if (c.access === 'derived') nm = '/' + nm;
          lines.push('    ' + colType(c.type) + ' ' + nm);
        });
      lines.push('  }');
    });
    (catalog.fks || []).forEach(function (f) {
      var sk = f.src_schema + '.' + f.src_table;
      var tk = f.tgt_schema + '.' + f.tgt_table;
      if (keys[sk] && keys[tk]) {
        lines.push('  ' + entName(f.tgt_schema, f.tgt_table) + ' "1..1" -- "0..*" ' +
          entName(f.src_schema, f.src_table) + ' : ' + f.src_column);
      }
    });
    var def = lines.join('\n');

    var erdDiv = document.createElement('div');
    erdDiv.className = 'portal-erd';
    container.innerHTML = '';
    container.appendChild(erdDiv);

    if (!tables.length) {
      erdDiv.innerHTML = '<p class="portal-empty">No tables in scope.</p>';
    } else {
      mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' });
      var id = 'portal-erd-' + Math.random().toString(36).slice(2);
      var done = function (svg) {
        // Straighten edges: Mermaid draws cubic beziers; rewriting each C
        // command as L segments through its control points gives the
        // straight orthogonal lines used in class-style UML diagrams.
        svg = svg.replace(/d="([^"]+)"/g, function (m, d) {
          return 'd="' + d.replace(/C/g, 'L') + '"';
        });
        erdDiv.innerHTML = svg;
      };
      var fail = function (e) {
        erdDiv.innerHTML = '<div class="portal-error"><strong>Diagram error.</strong> Could not render the schema map.</div>';
        if (window.console) console.error(e);
      };
      try {
        var out = mermaid.render(id, def);
        if (out && typeof out.then === 'function') out.then(function (r) { done(r.svg); }).catch(fail);
        else done(out.svg || out);
      } catch (e) { fail(e); }
    }

    renderDictionary(container, catalog, opts);
  }

  function renderDictionary(container, catalog, opts) {
    opts = opts || {};
    var schemas = opts.schemas || null;
    var inScope = function (s) { return !schemas || schemas.indexOf(s) !== -1; };
    var tables = (catalog.tables || []).filter(function (t) { return inScope(t.schema); });
    var cols = (catalog.columns || []).filter(function (c) { return inScope(c.schema); });
    var tableMeta = {};
    tables.forEach(function (t) { tableMeta[t.schema + '.' + t.table] = t; });

    var wrap = document.createElement('div');
    wrap.className = 'portal-dict';
    var rows = cols
      .sort(function (a, b) {
        var ka = a.schema + '.' + a.table, kb = b.schema + '.' + b.table;
        return ka === kb ? (a.ordinal || 0) - (b.ordinal || 0) : (ka < kb ? -1 : 1);
      })
      .map(function (c) {
        var t = tableMeta[c.schema + '.' + c.table];
        return {
          table: c.schema + '.' + c.table,
          column: c.column,
          type: c.type,
          access: c.access,
          desc: (t && t.description) || ''
        };
      });

    wrap.innerHTML =
      '<input type="search" class="dict-search" placeholder="Search tables & columns\u2026">' +
      '<div class="portal-table-wrap"><table class="portal-table dict-table"><thead><tr>' +
      '<th>Table</th><th>Column</th><th>Type</th><th>Access</th><th>Table description</th>' +
      '</tr></thead><tbody></tbody></table></div>';
    var tbody = wrap.querySelector('tbody');

    function accessCell(a) {
      return a === 'derived'
        ? '<span class="badge-derived">trend-only</span>'
        : esc(a || '');
    }

    function draw(filter) {
      var f = (filter || '').toLowerCase();
      var shown = rows.filter(function (r) {
        return !f || (r.table + ' ' + r.column + ' ' + (r.type || '') + ' ' + r.desc).toLowerCase().indexOf(f) !== -1;
      });
      tbody.innerHTML = shown.map(function (r) {
        return '<tr><td><code>' + esc(r.table) + '</code></td><td>' + esc(r.column) + '</td><td><code>' +
          esc(r.type) + '</code></td><td>' + accessCell(r.access) + '</td><td class="dict-desc">' +
          esc(r.desc) + '</td></tr>';
      }).join('') || '<tr><td colspan="5" class="portal-empty">No matches.</td></tr>';
    }
    draw('');
    wrap.querySelector('.dict-search').addEventListener('input', function () { draw(this.value); });
    container.appendChild(wrap);
  }

  return {
    lineChart: lineChart,
    barChart: barChart,
    stackedBar: stackedBar,
    stackedBarTime: stackedBarTime,
    cellChart: cellChart,
    groupedBar: groupedBar,
    scatter: scatter,
    table: table,
    renderErd: renderErd
  };
})();
