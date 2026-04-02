'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Sparkles,
  SearchCode,
  BarChart3,
  FileText,
  ArrowRight,
  RefreshCcw,
  AlertCircle,
  BrainCircuit
} from 'lucide-react';
import AgentBadge from './components/AgentBadge';
import AnimatedReport from './components/AnimatedReport';

export default function Home() {
  const [topic, setTopic] = useState('');
  const [report, setReport] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Agent Status Simulation
  const [researcherStatus, setResearcherStatus] = useState<'idle' | 'working' | 'completed'>('idle');
  const [analystStatus, setAnalystStatus] = useState<'idle' | 'working' | 'completed'>('idle');
  const [writerStatus, setWriterStatus] = useState<'idle' | 'working' | 'completed'>('idle');

  // Handle simulation timing when loading starts
  useEffect(() => {
    if (loading) {
      setResearcherStatus('working');
      setAnalystStatus('idle');
      setWriterStatus('idle');

      // Typical CrewAI sequence simulation
      const analystTimer = setTimeout(() => {
        setResearcherStatus('completed');
        setAnalystStatus('working');
      }, 5000);

      const writerTimer = setTimeout(() => {
        setAnalystStatus('completed');
        setWriterStatus('working');
      }, 12000);

      return () => {
        clearTimeout(analystTimer);
        clearTimeout(writerTimer);
      };
    } else if (report) {
      setResearcherStatus('completed');
      setAnalystStatus('completed');
      setWriterStatus('completed');
    } else {
      setResearcherStatus('idle');
      setAnalystStatus('idle');
      setWriterStatus('idle');
    }
  }, [loading, report]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setLoading(true);
    setReport('');
    setError('');

    try {
      // แก้ไขบรรทัด fetch ในไฟล์ page.tsx ให้เป็นแบบนี้:
      const response = await fetch('https://ai-research-backend-drga.onrender.com/api/generate-report/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'API connection failed');
      }

      setReport(data.report);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative min-h-screen pt-20 pb-20 px-4 overflow-x-hidden">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/5 blur-[120px] rounded-full" />
        <div className="absolute bottom-[10%] right-[-10%] w-[35%] h-[35%] bg-purple-600/5 blur-[120px] rounded-full" />
      </div>

      <div className="max-w-4xl mx-auto">
        {/* Header Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16 space-y-6"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold uppercase tracking-widest mb-4">
            <BrainCircuit size={14} />
            <span>Next-Gen Multi-Agent intelligence</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight">
            <span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60">AI Research</span>
            <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500 glow-text">Assistant</span>
          </h1>

          <p className="max-w-xl mx-auto text-slate-400 text-lg md:text-xl font-medium">
            ระบบวิเคราะห์และสรุปข้อมูลอัจฉริยะด้วยทีม AI Agent นักวิจัย วิเคราะห์ และนักเขียนมืออาชีพ
          </p>
        </motion.div>

        {/* Search & Agent Status Section */}
        <div className="space-y-8 mb-12">
          {/* Main Input Form */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-panel p-2 rounded-2xl md:rounded-3xl shadow-xl overflow-hidden"
          >
            <form onSubmit={handleGenerate} className="flex items-center gap-2 md:gap-4 p-1 md:p-2 bg-black/20 rounded-xl md:rounded-2xl border border-white/5">
              <div className="pl-4 md:pl-6 text-slate-500">
                <Search size={22} />
              </div>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="ค้นหาอย่างล้ำลึก เช่น แนวโน้มตลาด Clean Energy 2025..."
                className="flex-1 bg-transparent px-2 py-4 md:py-5 outline-none text-white text-lg placeholder:text-slate-600 font-medium"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !topic.trim()}
                className="group relative flex items-center gap-2 px-6 md:px-8 py-3 md:py-4 rounded-xl md:rounded-2xl bg-gradient-to-r from-blue-600 to-blue-500 font-bold text-white shadow-lg shadow-blue-500/25 transition-all hover:shadow-blue-500/40 hover:scale-[1.02] active:scale-95 disabled:opacity-50 disabled:grayscale disabled:cursor-not-allowed overflow-hidden"
              >
                <div className="absolute inset-0 bg-white/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                <span className="relative z-10">{loading ? 'กำลังประมวลผล' : 'เริ่มการค้นหา'}</span>
                {!loading && <ArrowRight size={18} className="relative z-10 transition-transform group-hover:translate-x-1" />}
                {loading && <RefreshCcw size={18} className="relative z-10 animate-spin" />}
              </button>
            </form>
          </motion.div>

          {/* Error Message */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl flex items-center gap-3"
              >
                <AlertCircle size={18} />
                <span className="text-sm font-medium">{error}</span>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Multi-Agent Status Display */}
          <div className="flex flex-wrap justify-center gap-4 md:gap-8 py-4">
            <AgentBadge
              icon={SearchCode}
              name="Researcher"
              status={researcherStatus}
              color="blue"
            />
            <div className="h-4 w-px bg-white/10 hidden md:block self-center" />
            <AgentBadge
              icon={BarChart3}
              name="Analyst"
              status={analystStatus}
              color="purple"
            />
            <div className="h-4 w-px bg-white/10 hidden md:block self-center" />
            <AgentBadge
              icon={FileText}
              name="Writer"
              status={writerStatus}
              color="emerald"
            />
          </div>
        </div>

        {/* Results Area */}
        <AnimatePresence mode="wait">
          {report ? (
            <AnimatedReport content={report} key="report" />
          ) : loading ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center p-20 text-center space-y-6"
            >
              <div className="relative">
                <div className="w-20 h-20 rounded-full border-2 border-blue-500/20 border-t-blue-500 animate-spin" />
                <Sparkles className="absolute inset-0 m-auto text-blue-400 animate-pulse" size={24} />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-bold text-white tracking-tight">AI กำลังทำงานผสานกันอย่างเป็นระบบ</h3>
                <p className="text-slate-500 text-sm max-w-xs mx-auto">
                  การค้นหาข้อมูลเชิงลึกอาจใช้เวลาสักครู่ เพื่อผลลัพธ์ที่มีคุณภาพสูงสุดสำหรับคุณ
                </p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6 opacity-40 pointer-events-none"
            >
              {[1, 2].map((i) => (
                <div key={i} className="glass-panel p-6 h-40 rounded-3xl border-dashed border-white/5 flex flex-col justify-end">
                  <div className="h-3 w-3/4 bg-white/5 rounded-full mb-3" />
                  <div className="h-3 w-1/2 bg-white/5 rounded-full" />
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <footer className="mt-20 text-center text-slate-600 text-sm font-medium">
        Powered by CrewAI, Tavily & Gemini Pro
      </footer>
    </main>
  );
}