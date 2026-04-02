'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  Check, 
  Copy, 
  Clock, 
  Target, 
  TrendingUp, 
  Award, 
  Lightbulb, 
  ChevronRight,
  Table as TableIcon,
  Info
} from 'lucide-react';

interface AnimatedReportProps {
  content: string;
}

const getHeaderIcon = (text: string) => {
  const t = text.toLowerCase();
  if (t.includes('ทักษะ') || t.includes('skill')) return <Award className="text-blue-400" size={24} />;
  if (t.includes('ความสำคัญ') || t.includes('important')) return <TrendingUp className="text-purple-400" size={24} />;
  if (t.includes('เป้าหมาย') || t.includes('goal')) return <Target className="text-emerald-400" size={24} />;
  if (t.includes('สรุป') || t.includes('summary') || t.includes('verdict')) return <Lightbulb className="text-amber-400" size={24} />;
  return <ChevronRight className="text-slate-500" size={20} />;
};

export default function AnimatedReport({ content }: AnimatedReportProps) {
  const [copied, setCopied] = useState(false);

  const readingTime = useMemo(() => {
    const wordsPerMinute = 200;
    const numberOfWords = content.split(/\s/g).length;
    return Math.ceil(numberOfWords / wordsPerMinute);
  }, [content]);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="glass-panel p-6 md:p-10 rounded-[2.5rem] border-white/10 shadow-2xl overflow-hidden relative"
    >
      {/* Decorative gradient corner */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 blur-[100px] -mr-32 -mt-32 rounded-full pointer-events-none" />
      
      {/* Top Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-10 pb-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
          <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 tracking-tight">
            Analysis Report
          </h2>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/5 text-[11px] font-bold text-slate-400 uppercase tracking-widest">
            <Clock size={14} className="text-blue-400" />
            <span>{readingTime} min read</span>
          </div>
          
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/20 text-[11px] font-bold text-blue-400 uppercase tracking-widest transition-all active:scale-95"
          >
            {copied ? (
              <><Check size={14} /> <span>Copied</span></>
            ) : (
              <><Copy size={14} /> <span>Copy Markdown</span></>
            )}
          </button>
        </div>
      </div>

      {/* Styled Content */}
      <article className="prose prose-invert prose-blue max-w-none 
        prose-headings:tracking-tight prose-headings:font-extrabold
        prose-p:text-slate-300 prose-p:leading-relaxed
        prose-strong:text-white prose-strong:font-bold
        prose-table:my-8 prose-pre:bg-black/40 prose-pre:border prose-pre:border-white/5
      ">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            h2: ({node, ...props}) => (
              <div className="group flex items-center gap-3 mt-14 mb-6 first:mt-0">
                <div className="p-2 rounded-xl bg-white/5 border border-white/5 transition-colors group-hover:bg-blue-500/10 group-hover:border-blue-500/20">
                  {getHeaderIcon(props.children as string)}
                </div>
                <h2 className="m-0 text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 transition-all group-hover:to-white">
                  {props.children}
                </h2>
              </div>
            ),
            h3: ({node, ...props}) => (
              <h3 className="flex items-center gap-2 mt-8 mb-4 text-xl font-bold text-blue-300/90 border-l-2 border-blue-500/30 pl-4">
                {props.children}
              </h3>
            ),
            table: ({node, ...props}) => (
              <div className="my-10 overflow-hidden rounded-2xl border border-white/10 bg-white/[0.02] backdrop-blur-sm shadow-xl">
                <div className="flex items-center gap-2 p-4 bg-white/[0.05] border-b border-white/10">
                  <TableIcon size={16} className="text-blue-400" />
                  <span className="text-[10px] uppercase font-bold tracking-widest text-slate-400">Comparison Data</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="m-0" {...props} />
                </div>
              </div>
            ),
            ul: ({node, ...props}) => (
              <ul className="my-6 space-y-3 list-none pl-0" {...props} />
            ),
            li: ({node, ...props}) => (
              <li className="relative pl-7 text-slate-300">
                <span className="absolute left-0 top-[0.6em] w-4 h-[2px] bg-blue-500/40 rounded-full" />
                {props.children}
              </li>
            ),
            blockquote: ({node, ...props}) => (
              <div className="my-8 p-6 rounded-2xl bg-blue-500/5 border-l-4 border-blue-500/50 flex gap-4">
                <Info className="flex-shrink-0 text-blue-400 mt-1" size={20} />
                <blockquote className="m-0 p-0 border-none italic text-slate-300" {...props} />
              </div>
            )
          }}
        >
          {content}
        </ReactMarkdown>
      </article>

      {/* Footer Info */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-16 pt-8 border-t border-white/5 flex flex-wrap justify-between items-center gap-4 text-[10px] uppercase tracking-[0.2em] text-slate-500 font-black"
      >
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
            <span>AI Research Protocol v2.5</span>
          </div>
          <div className="w-px h-3 bg-white/10" />
          <span>Multi-Agent Architecture</span>
        </div>
        <span>© {new Date().getFullYear()} Insight Engine</span>
      </motion.div>
    </motion.div>
  );
}
