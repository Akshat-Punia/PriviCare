"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import ThemeToggle from "@/components/ThemeToggle";
import PatientSearchModal from "@/components/PatientSearchModal";
import { Menu, LogOut, User, Search } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="w-10 h-10 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col min-h-screen lg:min-w-0">
        {/* Top Bar */}
        <header className="sticky top-0 z-30 h-16 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-4 lg:px-6">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <span>🧠 PriviCare</span>
              <span className="hidden md:inline-block text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950 text-blue-800 dark:text-blue-300">
                Doctor Clinical Suite
              </span>
            </h1>
          </div>

          <div className="flex items-center gap-3">
            {/* Quick Patient Search Button */}
            <button
              onClick={() => setSearchOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/80 hover:bg-gray-100 dark:hover:bg-gray-800 text-xs font-medium text-gray-700 dark:text-gray-300 shadow-sm transition-all"
              title="Search patient directory (Ctrl+K)"
            >
              <Search className="w-3.5 h-3.5 text-primary-600 dark:text-primary-400" />
              <span className="hidden sm:inline">Search Patient</span>
              <kbd className="hidden lg:inline-block px-1.5 py-0.5 text-[10px] font-mono text-gray-400 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded">
                Ctrl+K
              </kbd>
            </button>

            <ThemeToggle />

            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-gray-100 dark:bg-gray-800">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                <User className="w-3.5 h-3.5 text-white" />
              </div>
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {user?.username || "User"}
              </span>
            </div>

            <button
              onClick={() => {
                logout();
                router.push("/login");
              }}
              className="p-2.5 rounded-xl hover:bg-red-50 dark:hover:bg-red-950/30 text-gray-500 hover:text-red-600 dark:hover:text-red-400 transition-all duration-200"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 p-4 lg:p-6">{children}</main>
        <PatientSearchModal isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
      </div>
    </div>
  );
}
