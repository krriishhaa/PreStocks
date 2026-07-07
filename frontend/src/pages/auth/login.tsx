import React from "react";
import Head from "next/head";
import Link from "next/link";
import { LoginForm } from "@/components/auth/LoginForm";

export default function LoginPage() {
  return (
    <>
      <Head>
        <title>Sign In - PreStocks</title>
      </Head>
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center px-4">
        <div className="w-full max-w-sm">
          <div className="text-center mb-8">
            <h1 className="text-[24px] font-bold text-[#1F2937] mb-1">Welcome back</h1>
            <p className="text-[14px] text-[#9CA3AF]">Sign in to your account</p>
          </div>

          <div className="bg-white p-6 rounded-[8px] border border-[#E5E7EB] shadow-[0px_1px_3px_rgba(0,0,0,0.1)]">
            <LoginForm />
          </div>

          <p className="mt-4 text-center text-[13px] text-[#9CA3AF]">
            Don&apos;t have an account?{" "}
            <Link href="/auth/signup" className="text-[#1E40AF] font-medium hover:underline">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </>
  );
}
