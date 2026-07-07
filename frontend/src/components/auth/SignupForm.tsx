import React, { useState } from "react";
import { useRouter } from "next/router";
import { useForm } from "react-hook-form";
import { Button } from "@/components/common/Button";
import { api } from "@/utils/api";

interface SignupData {
  full_name: string;
  email: string;
  password: string;
  confirm_password: string;
}

export function SignupForm() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<SignupData>();

  const password = watch("password");

  const onSubmit = async (data: SignupData) => {
    setError("");
    setIsLoading(true);
    try {
      const res = await api.post("/auth/signup", {
        email: data.email,
        password: data.password,
        full_name: data.full_name,
      });

      // Store tokens from signup response
      localStorage.setItem("ps_token", res.data.access_token);
      localStorage.setItem("ps_refresh_token", res.data.refresh_token);

      // Redirect to dashboard (they can do risk assessment later)
      router.push("/app/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
      {error && (
        <div className="p-3 rounded-md bg-red-50 border border-red-200 text-sm text-red-700">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="full_name" className="block text-sm font-medium text-neutral-700 mb-1">
          Full Name
        </label>
        <input
          id="full_name"
          type="text"
          autoComplete="name"
          className="w-full px-3 py-2 border border-neutral-200 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-800/20 focus:border-primary-800"
          placeholder="Jane Doe"
          {...register("full_name", { required: "Name is required" })}
        />
        {errors.full_name && <p className="text-xs text-red-500 mt-1">{errors.full_name.message}</p>}
      </div>

      <div>
        <label htmlFor="signup_email" className="block text-sm font-medium text-neutral-700 mb-1">
          Email
        </label>
        <input
          id="signup_email"
          type="email"
          autoComplete="email"
          className="w-full px-3 py-2 border border-neutral-200 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-800/20 focus:border-primary-800"
          placeholder="you@example.com"
          {...register("email", {
            required: "Email is required",
            pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: "Invalid email" },
          })}
        />
        {errors.email && <p className="text-xs text-red-500 mt-1">{errors.email.message}</p>}
      </div>

      <div>
        <label htmlFor="signup_password" className="block text-sm font-medium text-neutral-700 mb-1">
          Password
        </label>
        <input
          id="signup_password"
          type="password"
          autoComplete="new-password"
          className="w-full px-3 py-2 border border-neutral-200 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-800/20 focus:border-primary-800"
          placeholder="Min 8 characters"
          {...register("password", {
            required: "Password is required",
            minLength: { value: 8, message: "Must be at least 8 characters" },
          })}
        />
        {errors.password && <p className="text-xs text-red-500 mt-1">{errors.password.message}</p>}
      </div>

      <div>
        <label htmlFor="confirm_password" className="block text-sm font-medium text-neutral-700 mb-1">
          Confirm Password
        </label>
        <input
          id="confirm_password"
          type="password"
          autoComplete="new-password"
          className="w-full px-3 py-2 border border-neutral-200 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-800/20 focus:border-primary-800"
          placeholder="••••••••"
          {...register("confirm_password", {
            required: "Please confirm your password",
            validate: (val) => val === password || "Passwords do not match",
          })}
        />
        {errors.confirm_password && (
          <p className="text-xs text-red-500 mt-1">{errors.confirm_password.message}</p>
        )}
      </div>

      <Button type="submit" variant="primary" size="lg" loading={isLoading} className="w-full mt-2">
        Create Account
      </Button>

      <p className="text-xs text-neutral-400 text-center mt-1">
        By creating an account you agree to our Terms of Service and Privacy Policy.
      </p>
    </form>
  );
}
