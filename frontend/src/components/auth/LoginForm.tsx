import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/common/Button";
import { useAuth } from "@/hooks/useAuth";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});

type LoginData = z.infer<typeof loginSchema>;

export function LoginForm() {
  const { login, isLoading, error } = useAuth();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginData>({ resolver: zodResolver(loginSchema) });

  const onSubmit = (data: LoginData) => {
    login(data.email, data.password);
  };

  return (
    <div className="flex flex-col gap-5">
      {/* SSO Buttons */}
      <div className="flex flex-col gap-2">
        <button className="w-full h-10 flex items-center justify-center gap-2 rounded-[6px] border border-[#E5E7EB] bg-white text-[14px] font-medium text-[#1F2937] hover:bg-[#F8FAFC] transition-colors">
          <svg className="w-4 h-4" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continue with Google
        </button>
        <button className="w-full h-10 flex items-center justify-center gap-2 rounded-[6px] border border-[#E5E7EB] bg-white text-[14px] font-medium text-[#1F2937] hover:bg-[#F8FAFC] transition-colors">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
          </svg>
          Continue with Apple
        </button>
      </div>

      <div className="flex items-center gap-3">
        <hr className="flex-1 border-[#E5E7EB]" />
        <span className="text-[12px] text-[#9CA3AF]">or</span>
        <hr className="flex-1 border-[#E5E7EB]" />
      </div>

      {/* Email/Password Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <label className="text-[13px] font-medium text-[#9CA3AF]">Email</label>
          <input
            type="email"
            {...register("email")}
            className="h-10 px-3 rounded-[6px] border border-[#E5E7EB] bg-white text-[14px] text-[#1F2937] placeholder:text-[#9CA3AF] transition-all focus:outline-none focus:border-[#1E40AF] focus:shadow-[0px_1px_2px_rgba(0,0,0,0.05)]"
            placeholder="you@example.com"
          />
          {errors.email && (
            <span className="text-[12px] text-[#EF4444]">{errors.email.message}</span>
          )}
        </div>

        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <label className="text-[13px] font-medium text-[#9CA3AF]">Password</label>
            <a href="#" className="text-[12px] text-[#1E40AF] hover:underline">Forgot?</a>
          </div>
          <input
            type="password"
            {...register("password")}
            className="h-10 px-3 rounded-[6px] border border-[#E5E7EB] bg-white text-[14px] text-[#1F2937] placeholder:text-[#9CA3AF] transition-all focus:outline-none focus:border-[#1E40AF] focus:shadow-[0px_1px_2px_rgba(0,0,0,0.05)]"
            placeholder="••••••••"
          />
          {errors.password && (
            <span className="text-[12px] text-[#EF4444]">{errors.password.message}</span>
          )}
        </div>

        {error && (
          <div className="p-3 rounded-[6px] bg-[rgba(239,68,68,0.1)] border border-[#EF4444]/30 text-[13px] text-[#EF4444]">
            {error}
          </div>
        )}

        <Button type="submit" variant="primary" size="lg" loading={isLoading} className="w-full mt-1">
          Sign In
        </Button>
      </form>

      <p className="text-[11px] text-[#9CA3AF] text-center">
        We recommend enabling 2FA for account security.
      </p>
    </div>
  );
}
