"use client";
import { useState, useEffect, useRef } from "react";
import useSWR from "swr";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const fetcher = (url: string) => fetch(url).then((r) => r.json());

export default function Dashboard() {
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [selectedTicker, setSelectedTicker] = useState("TSLA");
  const [livePosts, setLivePosts] = useState<any[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const { data: posts } = useSWR(
    `${API}/api/posts?q=${search}&limit=50`,
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

  useEffect(() => {
    const wsUrl = API.replace("http", "ws") + "/ws/live-feed";
    wsRef.current = new WebSocket(wsUrl);
    wsRef.current.onmessage = (e) => {
      try {
        const post = JSON.parse(e.data);
        setLivePosts((prev) => [post, ...prev].slice(0, 50));
      } catch {}
    };
    return () => wsRef.current?.close();
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-white">Social Tracker</h1>

      {/* Search */}
      <div className="flex gap-2 mb-8">
        <input
          className="flex-1 bg-gray-800 border border-gray-700 rounded px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          placeholder="Search posts..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && setSearch(query)}
        />
        <button
          className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded text-white font-medium"
          onClick={() => setSearch(query)}
        >
          Search
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Trending Stocks */}
        <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
          <h2 className="text-lg font-semibold mb-3 text-gray-200">Trending Stocks (24h)</h2>
          <div className="space-y-2">
            {(trending || []).map((t: any) => (
              <button
                key={t.ticker}
                className={`w-full flex justify-between items-center px-3 py-2 rounded-lg text-sm transition-colors ${selectedTicker === t.ticker ? "bg-blue-900 border border-blue-700" : "bg-gray-800 hover:bg-gray-700"}`}
                onClick={() => setSelectedTicker(t.ticker)}
              >
                <span className="font-mono font-bold text-white">${t.ticker}</span>
                <div className="flex items-center gap-3">
                  <span className="text-gray-400">{t.mention_count} mentions</span>
                  <span className={t.avg_sentiment > 0.05 ? "text-green-400" : t.avg_sentiment < -0.05 ? "text-red-400" : "text-gray-400"}>
                    {t.avg_sentiment > 0 ? "+" : ""}{t.avg_sentiment?.toFixed(2)}
                  </span>
                </div>
              </button>
            ))}
            {!trending?.length && <p className="text-gray-500 text-sm text-center py-4">No data yet — scrapers starting up</p>}
          </div>
        </div>

        {/* Sentiment Chart */}
        <div className="bg-gray-900 rounded-xl p-4 border border-gray-800 col-span-2">
          <h2 className="text-lg font-semibold mb-3 text-gray-200">
            Sentiment Timeline — <span className="text-blue-400">${selectedTicker}</span>
          </h2>
          {sentiment?.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={sentiment}>
                <XAxis dataKey="hour" tickFormatter={(v) => v.slice(11, 16)} stroke="#6b7280" tick={{ fontSize: 11 }} />
                <YAxis domain={[-1, 1]} stroke="#6b7280" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: "#1f2937", border: "1px solid #374151", borderRadius: 8 }}
                  labelStyle={{ color: "#9ca3af" }}
                />
                <Line type="monotone" dataKey="avg_sentiment" stroke="#3b82f6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-52 flex items-center justify-center text-gray-500 text-sm">
              No sentiment data yet for ${selectedTicker}
            </div>
          )}
        </div>

        {/* Live Feed */}
        <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
          <h2 className="text-lg font-semibold mb-3 text-gray-200">
            Live Feed <span className="inline-block w-2 h-2 bg-green-400 rounded-full animate-pulse ml-1"></span>
          </h2>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {livePosts.map((p, i) => (
              <div key={i} className="bg-gray-800 rounded p-2 text-xs">
                <div className="flex justify-between text-gray-500 mb-1">
                  <span className="capitalize">{p.source}</span>
                  <span>{p.author}</span>
                </div>
                <p className="text-gray-300 line-clamp-2">{p.content}</p>
              </div>
            ))}
            {!livePosts.length && <p className="text-gray-500 text-sm text-center py-4">Waiting for live data...</p>}
          </div>
        </div>

        {/* Search Results */}
        <div className="bg-gray-900 rounded-xl p-4 border border-gray-800 col-span-2">
          <h2 className="text-lg font-semibold mb-3 text-gray-200">
            {search ? `Results for "${search}"` : "Recent Posts"}
          </h2>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {(posts || []).map((p: any) => (
              <div key={p.id} className="bg-gray-800 rounded-lg p-3">
                <div className="flex justify-between items-center mb-1 text-xs text-gray-500">
                  <span className="capitalize font-medium text-gray-400">{p.source}</span>
                  <span>{p.author} · {p.posted_at ? new Date(p.posted_at).toLocaleString() : ""}</span>
                </div>
                <p className="text-sm text-gray-200 line-clamp-3">{p.content}</p>
                {p.url && (
                  <a href={p.url} target="_blank" rel="noreferrer" className="text-xs text-blue-400 hover:underline mt-1 inline-block">
                    View source
                  </a>
                )}
              </div>
            ))}
            {!posts?.length && <p className="text-gray-500 text-sm text-center py-4">No posts yet</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
