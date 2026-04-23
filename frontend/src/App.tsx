import { useState, useEffect } from 'react'
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import { Activity, ShieldCheck, Cpu, Database } from 'lucide-react'

const queryClient = new QueryClient()

function HealthStatus() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await fetch('/api/health')
      if (!response.ok) {
        throw new Error('Network response was not ok')
      }
      return response.json()
    }
  })

  return (
    <div className="p-6 max-w-md mx-auto bg-slate-900 rounded-xl shadow-2xl border border-slate-800 backdrop-blur-sm">
      <div className="flex items-center gap-3 mb-6">
        <Activity className="text-cyan-400 animate-pulse" size={24} />
        <h2 className="text-xl font-bold text-white tracking-tight">System Status</h2>
      </div>

      <div className="space-y-4">
        <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
          <span className="text-slate-400">Backend Status</span>
          {isLoading ? (
            <span className="text-amber-400 text-sm">Checking...</span>
          ) : error ? (
            <span className="text-rose-500 text-sm font-medium">Offline</span>
          ) : (
            <span className="flex items-center gap-1.5 text-emerald-400 text-sm font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              {data?.status}
            </span>
          )}
        </div>

        <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
          <span className="text-slate-400">API Version</span>
          <span className="text-cyan-300 font-mono text-xs">
            {isLoading ? "---" : data?.version || "unknown"}
          </span>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen w-full flex flex-col items-center justify-center bg-[#020617] text-white p-4">
        <div className="max-w-4xl w-full space-y-12">
          <header className="text-center space-y-4">
            <div className="inline-flex items-center justify-center p-3 bg-gradient-to-tr from-cyan-500 to-blue-600 rounded-2xl mb-4 shadow-lg shadow-blue-500/20">
              <Cpu size={48} className="text-white" />
            </div>
            <h1 className="text-6xl font-black tracking-tighter bg-gradient-to-b from-white to-slate-400 bg-clip-text text-transparent">
              FINSIGHT AI
            </h1>
            <p className="text-slate-400 text-lg max-w-xl mx-auto font-medium">
              Enterprise-grade financial intelligence powered by Claude & XGBoost.
            </p>
          </header>

          <main className="grid md:grid-cols-2 gap-8 items-start">
            <HealthStatus />
            
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
                  <ShieldCheck className="text-indigo-400 mb-2" size={20} />
                  <h3 className="font-bold text-sm">Supabase</h3>
                  <p className="text-xs text-slate-500">RLS & Auth enabled</p>
                </div>
                <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
                  <Database className="text-blue-400 mb-2" size={20} />
                  <h3 className="font-bold text-sm">PostgreSQL</h3>
                  <p className="text-xs text-slate-500">Real-time sync</p>
                </div>
              </div>
              
              <div className="p-6 bg-gradient-to-r from-slate-900 to-slate-900 border border-slate-800 rounded-xl">
                <h3 className="text-sm font-bold mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
                  ML Pipeline
                </h3>
                <div className="space-y-2">
                  <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full w-[85%] bg-indigo-500"></div>
                  </div>
                  <div className="flex justify-between text-[10px] font-mono text-slate-500 uppercase tracking-widest">
                    <span>Training Status</span>
                    <span>Ready</span>
                  </div>
                </div>
              </div>
            </div>
          </main>
          
          <footer className="text-center pt-8 border-t border-slate-900">
            <p className="text-slate-600 text-xs font-mono">
              v1.0.0-alpha • STACK: FASTAPI / REACT 19 / TAILWIND 4
            </p>
          </footer>
        </div>
      </div>
    </QueryClientProvider>
  )
}

export default App
