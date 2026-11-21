"use client";

import React from "react";

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: string;
  color: "blue" | "teal" | "green" | "purple" | "amber";
}

const colorMap = {
  blue: {
    bg: "bg-blue-50 dark:bg-blue-950/30",
    icon: "bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400",
    border: "border-blue-100 dark:border-blue-900/50",
  },
  teal: {
    bg: "bg-teal-50 dark:bg-teal-950/30",
    icon: "bg-teal-100 dark:bg-teal-900/50 text-teal-600 dark:text-teal-400",
    border: "border-teal-100 dark:border-teal-900/50",
  },
  green: {
    bg: "bg-green-50 dark:bg-green-950/30",
    icon: "bg-green-100 dark:bg-green-900/50 text-green-600 dark:text-green-400",
    border: "border-green-100 dark:border-green-900/50",
  },
  purple: {
    bg: "bg-purple-50 dark:bg-purple-950/30",
    icon: "bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-400",
    border: "border-purple-100 dark:border-purple-900/50",
  },
  amber: {
    bg: "bg-amber-50 dark:bg-amber-950/30",
    icon: "bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-400",
    border: "border-amber-100 dark:border-amber-900/50",
  },
};

export default function StatsCard({ title, value, icon, trend, color }: StatsCardProps) {
  const colors = colorMap[color];

  return (
    <div
      className={`${colors.bg} border ${colors.border} rounded-2xl p-6 transition-all duration-200 hover:shadow-lg hover:scale-[1.02]`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">{value}</p>
          {trend && (
            <p className="mt-1 text-xs font-medium text-green-600 dark:text-green-400">{trend}</p>
          )}
        </div>
        <div className={`p-3 rounded-xl ${colors.icon}`}>{icon}</div>
      </div>
    </div>
  );
}
