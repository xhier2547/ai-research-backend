'use client';

import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface AgentBadgeProps {
  icon: LucideIcon;
  name: string;
  status: 'idle' | 'working' | 'completed';
  color: 'blue' | 'purple' | 'emerald';
}

export default function AgentBadge({ icon: Icon, name, status, color }: AgentBadgeProps) {
  const colorMap = {
    blue: 'text-blue-400 border-blue-500/30 bg-blue-500/10',
    purple: 'text-purple-400 border-purple-500/30 bg-purple-500/10',
    emerald: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
  };

  const glowMap = {
    blue: 'shadow-[0_0_15px_rgba(59,130,246,0.5)]',
    purple: 'shadow-[0_0_15px_rgba(139,92,246,0.5)]',
    emerald: 'shadow-[0_0_15px_rgba(16,185,129,0.5)]',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "flex items-center gap-3 px-4 py-2 rounded-full border transition-all duration-500",
        colorMap[color],
        status === 'working' && glowMap[color]
      )}
    >
      <div className="relative">
        <Icon size={18} className={cn(status === 'working' && "animate-pulse")} />
        {status === 'working' && (
          <motion.div
            layoutId="active-glow"
            className="absolute -inset-1 rounded-full bg-current opacity-20 blur-sm"
            animate={{ scale: [1, 1.5, 1], opacity: [0.2, 0.4, 0.2] }}
            transition={{ repeat: Infinity, duration: 2 }}
          />
        )}
      </div>
      <div className="flex flex-col">
        <span className="text-xs font-bold uppercase tracking-wider">{name}</span>
        <span className={cn(
          "text-[10px] font-medium opacity-70",
          status === 'working' && "animate-pulse"
        )}>
          {status === 'idle' ? 'Ready' : status === 'working' ? 'Processing...' : 'Finished'}
        </span>
      </div>
    </motion.div>
  );
}
