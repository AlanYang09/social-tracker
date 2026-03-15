"use client";
import { useState, useEffect, useRef } from "react";
import useSWR from "swr";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";

const API = process.env.NEXT_PUBLIC_API_URL || "";
const fetcher = (url: string) => fetch(url).then((r) => r.json());

const SOURCES = ["all", "stocktwits", "reddit", "nitter", "news"] as const;
type Source = (typeof SOURCES)[number];
type ChartMode = "sentiment" | "velocity";

function SentimentBadge({ score, label }: { score: number | null; label: string | null }) {
  if (score === null) return null;
  const cls =
    score > 0.05
      ? "bg-green-900 text-green-300 border-green-700"
      : score < -0.05
      ? "bg-red-900 text-red-300 border-red-700"
      : "bg-gray-700 text-gray-400 border-gray-600";
  const icon = score > 0.05 ? "▲" : score < -0.05 ? "▼" : "—";
  return (
    <span className={`text-xs px-1.5 py-0.5 rounded border font-mono ${cls}`}>
      {icon} {score > 0 ? "+" : ""}{score.toFixed(2)}
    </span>
  );
}

function SourceBadge({ source }: { source: string }) {
  const colors: Record<string, string> = {
    stocktwits: "bg-purple-900 text-purple-300",
    reddit: "bg-orange-900 text-orange-300",
    nitter: "bg-sky-900 text-sky-300",
    news: "bg-emerald-900 text-emerald-300",
  };
  return (
    <span className={`text-xs px-1.5 py-0.5 rounded capitalize font-medium ${colors[source] ?? "bg-gray-700 text-gray-400"}`}>
      {source}
    </span>
  );
}

function timeAgo(iso: string) {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return new Date(iso).toLocaleDateString();
}

export default function Dashboard() {
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [source, setSource] = useState<Source>("all");
  const [selectedTicker, setSelectedTicker] = useState("TSLA");
  const [chartMode, setChartMode] = useState<ChartMode>("sentiment");
  const [livePosts, setLivePosts] = useState<any[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const sourceParam = source !== "all" ? `&source=${source}` : "";
  const searchParam = search ? `&q=${encodeURIComponent(search)}` : "";

  const { data: posts } = useSWR(
    `${API}/api/posts?limit=50${searchParam}${sourceParam}`,
    fetcher,
    { refreshInterval: 30000 }
  );

  const { data: trending } = useSWR(
    `${API}/api/trends/stocks?hours=24&limit=15`,
    fetcher,
    { refreshInterval: 30000 }
  );

  const { data: sentiment } = useSWR(
    `${API}/api/trends/sentiment?ticker=${selectedTicker}&hours=24`,
    fetcher,
    { refreshInterval: 60000 }
  );

  const { data: history } = useSWR(
    `${API}/api/trends/history?ticker=${selectedTicker}&hours=24`,
    fetcher,
    { refreshInterval: 60000 }
  );

  const { data: stats } = useSWR(
    `${API}/api/trends/stats`,
    fetcher,
    { refreshInterval: 60000 }
  );

  useEffect(() => {
    const base = API || `${window.location.protocol}//${window.location.host}`;
    const wsUrl = base.replace(/^https/, "wss").replace(/^http/, "ws") + "/ws/live-feed";
    const connect = () => {
      wsRef.current = new WebSocket(wsUrl);
      wsRef.current.onmessage = (e) => {
        try {
          const post = JSON.parse(e.data);
          setLivePosts((prev) => [post, ...prev].slice(0, 100));
        } catch {}
      };
      wsRef.current.onclose = () => setTimeout(connect, 3000);
    };
    connect();
    return () => wsRef.current?.close();
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white">Social Tracker</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Real-time sentiment across X, Reddit &amp; StockTwits
          </p>
        </div>
        {stats && (
          <div className="flex gap-4 text-right">
            <div>
              <div className="text-2xl font-bold text-white">{stats.total_posts?.toLocaleString()}</div>
              <div className="text-xs text-gray-500">posts collected</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-400">{stats.tickers_tracked}</div>
              <div className="text-xs text-gray-500">tickers tracked</div>
            </div>
          </div>
        )}
      </div>

      {/* Search + source filter */}
      <div className="flex flex-col sm:flex-row gap-2 mb-6">
        <div className="flex gap-1 bg-gray-900 border border-gray-700 rounded-lg p-1">
          {SOURCES.map((s) => (
            <button
              key={s}
              onClick={() => setSource(s)}
              className={`px-3 py-1.5 rounded-md text-sm capitalize transition-colors ${
                source === s ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white"
              }`}
            >
              {s}
              {s !== "all" && stats?.by_source?.[s] != null && (
                <span className="ml-1 text-xs opacity-70">
                  {stats.by_source[s].toLocaleString()}
                </span>
              )}
            </button>
          ))}
        </div>
        <div className="flex flex-1 gap-2">
          <input
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            placeholder="Search posts..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && setSearch(query)}
          />
          <button
            className="bg-blue-600 hover:bg-blue-700 px-5 py-2 rounded-lg text-white font-medium transition-colors"
            onClick={() => setSearch(query)}
          >
            Search
          </button>
          {search && (
            <button
              className="text-gray-400 hover:text-white px-3 py-2 text-sm"
              onClick={() => { setSearch(""); setQuery(""); }}
            >
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Trending Stocks */}
        <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
          <h2 className="text-lg font-semibold mb-3 text-gray-200">Trending Stocks <span className="text-xs text-gray-500 font-normal">24h</span></h2>
          <div className="space-y-1.5">
            {(trending || []).map((t: any) => (
              <button
                key={t.ticker}
                className={`w-full flex justify-between items-center px-3 py-2 rounded-lg text-sm transition-colors ${
                  selectedTicker === t.ticker
                    ? "bg-blue-900 border border-blue-700"
                    : "bg-gray-800 hover:bg-gray-750 border border-transparent"
                }`}
                onClick={() => setSelectedTicker(t.ticker)}
              >
                <span className="font-mono font-bold text-white">${t.ticker}</span>
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 text-xs">{t.mention_count}×</span>
                  <SentimentBadge score={t.avg_sentiment} label={null} />
                </div>
              </button>
            ))}
            {!trending?.length && (
              <div className="text-gray-500 text-sm text-center py-6">
                <div className="text-2xl mb-2">📊</div>
                Scrapers starting up — data coming soon
              </div>
            )}
          </div>
        </div>

        {/* Chart */}
        <div className="bg-gray-900 rounded-xl p-4 border border-gray-800 col-span-2">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-200">
              <span className="text-blue-400 font-mono">${selectedTicker}</span>
              <span className="text-xs text-gray-500 font-normal ml-2">24h</span>
            </h2>
            <div className="flex gap-1 bg-gray-800 rounded-lg p-1">
              {(["sentiment", "velocity"] as ChartMode[]).map((m) => (
                <button
                  key={m}
                  onClick={() => setChartMode(m)}
                  className={`px-3 py-1 rounded-md text-xs capitalize transition-colors ${
                    chartMode === m ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white"
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          {chartMode === "sentiment" ? (
            sentiment?.length ? (
              <ResponsiveContainer width="100%" height={230}>
                <LineChart data={sentiment} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                  <XAxis dataKey="hour" tickFormatter={(v) => v.slice(11, 16)} stroke="#374151" tick={{ fontSize: 11, fill: "#6b7280" }} />
                  <YAxis domain={[-1, 1]} stroke="#374151" tick={{ fontSize: 11, fill: "#6b7280" }} tickFormatter={(v) => v.toFixed(1)} />
                  <ReferenceLine y={0} stroke="#374151" strokeDasharray="3 3" />
                  <Tooltip
                    contentStyle={{ background: "#111827", border: "1px solid #1f2937", borderRadius: 8 }}
                    labelStyle={{ color: "#9ca3af", fontSize: 12 }}
                    formatter={(v: any) => [v.toFixed(3), "sentiment"]}
                    labelFormatter={(l) => l.slice(0, 16)}
                  />
                  <Line type="monotone" dataKey="avg_sentiment" stroke="#3b82f6" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-56 flex flex-col items-center justify-center text-gray-500 text-sm">
                <div className="text-3xl mb-2">📈</div>
                No sentiment data for <span className="font-mono text-gray-400">${selectedTicker}</span> yet
              </div>
            )
          ) : (
            history?.length ? (
              <ResponsiveContainer width="100%" height={230}>
                <LineChart data={history} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                  <XAxis dataKey="snapshot_at" tickFormatter={(v) => v.slice(11, 16)} stroke="#374151" tick={{ fontSize: 11, fill: "#6b7280" }} />
                  <YAxis stroke="#374151" tick={{ fontSize: 11, fill: "#6b7280" }} />
                  <Tooltip
                    contentStyle={{ background: "#111827", border: "1px solid #1f2937", borderRadius: 8 }}
                    labelStyle={{ color: "#9ca3af", fontSize: 12 }}
                    formatter={(v: any) => [v, "mentions/hr"]}
                    labelFormatter={(l) => l.slice(0, 16)}
                  />
                  <Line type="monotone" dataKey="mention_count" stroke="#a78bfa" strokeWidth={2} dot={false} activeDot={{ r: 4 }} name="mentions" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-56 flex flex-col items-center justify-center text-gray-500 text-sm">
                <div className="text-3xl mb-2">📊</div>
                No velocity snapshots yet — first snapshot runs at 15min mark
              </div>
            )
          )}
        </div>

        {/* Live Feed */}
        <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
          <h2 className="text-lg font-semibold mb-3 text-gray-200 flex items-center gap-2">
            Live Feed
            <span className="inline-block w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
            {livePosts.length > 0 && (
              <span className="text-xs text-gray-500 font-normal">{livePosts.length}</span>
            )}
          </h2>
          <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
            {livePosts.map((p, i) => (
              <div key={i} className="bg-gray-800 rounded-lg p-2.5 text-xs border border-gray-700/50">
                <div className="flex justify-between items-center mb-1 gap-1">
                  <SourceBadge source={p.source} />
                  <span className="text-gray-500 truncate max-w-[100px]">{p.author}</span>
                </div>
                <p className="text-gray-300 line-clamp-2 leading-relaxed">{p.content}</p>
              </div>
            ))}
            {!livePosts.length && (
              <div className="text-gray-500 text-sm text-center py-6">
                <div className="text-2xl mb-2">📡</div>
                Waiting for live data...
              </div>
            )}
          </div>
        </div>

        {/* Posts */}
        <div className="bg-gray-900 rounded-xl p-4 border border-gray-800 col-span-2">
          <h2 className="text-lg font-semibold mb-3 text-gray-200">
            {search ? (
              <>Results for <span className="text-blue-400">"{search}"</span></>
            ) : (
              "Recent Posts"
            )}
            {posts?.length > 0 && (
              <span className="text-xs text-gray-500 font-normal ml-2">{posts.length} shown</span>
            )}
          </h2>
          <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
            {(posts || []).map((p: any) => (
              <div key={p.id} className="bg-gray-800 rounded-lg p-3 border border-gray-700/50">
                <div className="flex justify-between items-center mb-1.5 gap-2">
                  <div className="flex items-center gap-1.5">
                    <SourceBadge source={p.source} />
                    <span className="text-xs text-gray-400">{p.author}</span>
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <SentimentBadge score={p.sentiment_score} label={p.sentiment_label} />
                    <span className="text-xs text-gray-600">{p.posted_at ? timeAgo(p.posted_at) : ""}</span>
                  </div>
                </div>
                <p className="text-sm text-gray-200 line-clamp-3 leading-relaxed">{p.content}</p>
                {p.url && (
                  <a
                    href={p.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-blue-400 hover:underline mt-1 inline-block"
                  >
                    View source ↗
                  </a>
                )}
              </div>
            ))}
            {!posts?.length && (
              <div className="text-gray-500 text-sm text-center py-6">
                <div className="text-2xl mb-2">🔍</div>
                {search ? `No posts matching "${search}"` : "No posts collected yet"}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
