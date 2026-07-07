"use client";

import * as React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
} from "recharts";
import { cn } from "@/lib/utils";

const CHART_COLORS = {
  primary: "#1E40AF",
  secondary: "#06B6D4",
  success: "#10B981",
  warning: "#F59E0B",
  alert: "#EF4444",
  neutral: "#9CA3AF",
};

interface ChartContainerProps {
  children: React.ReactNode;
  height?: number;
  className?: string;
}

function ChartContainer({ children, height = 300, className }: ChartContainerProps) {
  return (
    <div className={cn("w-full", className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        {children as React.ReactElement}
      </ResponsiveContainer>
    </div>
  );
}

interface BaseChartProps {
  data: Record<string, unknown>[];
  xKey: string;
  height?: number;
  className?: string;
  showGrid?: boolean;
  showLegend?: boolean;
}

interface LineChartWidgetProps extends BaseChartProps {
  lines: {
    dataKey: string;
    color?: string;
    name?: string;
    strokeWidth?: number;
    dashed?: boolean;
  }[];
}

function LineChartWidget({
  data,
  xKey,
  lines,
  height = 300,
  className,
  showGrid = true,
  showLegend = false,
}: LineChartWidgetProps) {
  return (
    <ChartContainer height={height} className={className}>
      <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />}
        <XAxis
          dataKey={xKey}
          tick={{ fontSize: 12, fill: "#9CA3AF" }}
          axisLine={{ stroke: "#E5E7EB" }}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 12, fill: "#9CA3AF" }}
          axisLine={false}
          tickLine={false}
        />
        <RechartsTooltip
          contentStyle={{
            backgroundColor: "#FFFFFF",
            border: "1px solid #E5E7EB",
            borderRadius: "8px",
            fontSize: "13px",
            boxShadow: "0px 4px 12px rgba(0,0,0,0.1)",
          }}
        />
        {showLegend && <Legend />}
        {lines.map((line) => (
          <Line
            key={line.dataKey}
            type="monotone"
            dataKey={line.dataKey}
            name={line.name || line.dataKey}
            stroke={line.color || CHART_COLORS.primary}
            strokeWidth={line.strokeWidth || 2}
            strokeDasharray={line.dashed ? "5 5" : undefined}
            dot={false}
            activeDot={{ r: 4, strokeWidth: 2 }}
          />
        ))}
      </LineChart>
    </ChartContainer>
  );
}

interface BarChartWidgetProps extends BaseChartProps {
  bars: {
    dataKey: string;
    color?: string;
    name?: string;
    stackId?: string;
  }[];
}

function BarChartWidget({
  data,
  xKey,
  bars,
  height = 300,
  className,
  showGrid = true,
  showLegend = false,
}: BarChartWidgetProps) {
  return (
    <ChartContainer height={height} className={className}>
      <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />}
        <XAxis
          dataKey={xKey}
          tick={{ fontSize: 12, fill: "#9CA3AF" }}
          axisLine={{ stroke: "#E5E7EB" }}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 12, fill: "#9CA3AF" }}
          axisLine={false}
          tickLine={false}
        />
        <RechartsTooltip
          contentStyle={{
            backgroundColor: "#FFFFFF",
            border: "1px solid #E5E7EB",
            borderRadius: "8px",
            fontSize: "13px",
            boxShadow: "0px 4px 12px rgba(0,0,0,0.1)",
          }}
        />
        {showLegend && <Legend />}
        {bars.map((bar) => (
          <Bar
            key={bar.dataKey}
            dataKey={bar.dataKey}
            name={bar.name || bar.dataKey}
            fill={bar.color || CHART_COLORS.primary}
            stackId={bar.stackId}
            radius={[4, 4, 0, 0]}
          />
        ))}
      </BarChart>
    </ChartContainer>
  );
}

interface AreaChartWidgetProps extends BaseChartProps {
  areas: {
    dataKey: string;
    color?: string;
    name?: string;
    fillOpacity?: number;
    stackId?: string;
  }[];
}

function AreaChartWidget({
  data,
  xKey,
  areas,
  height = 300,
  className,
  showGrid = true,
  showLegend = false,
}: AreaChartWidgetProps) {
  return (
    <ChartContainer height={height} className={className}>
      <AreaChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />}
        <XAxis
          dataKey={xKey}
          tick={{ fontSize: 12, fill: "#9CA3AF" }}
          axisLine={{ stroke: "#E5E7EB" }}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 12, fill: "#9CA3AF" }}
          axisLine={false}
          tickLine={false}
        />
        <RechartsTooltip
          contentStyle={{
            backgroundColor: "#FFFFFF",
            border: "1px solid #E5E7EB",
            borderRadius: "8px",
            fontSize: "13px",
            boxShadow: "0px 4px 12px rgba(0,0,0,0.1)",
          }}
        />
        {showLegend && <Legend />}
        {areas.map((area) => (
          <Area
            key={area.dataKey}
            type="monotone"
            dataKey={area.dataKey}
            name={area.name || area.dataKey}
            stroke={area.color || CHART_COLORS.primary}
            fill={area.color || CHART_COLORS.primary}
            fillOpacity={area.fillOpacity || 0.1}
            stackId={area.stackId}
          />
        ))}
      </AreaChart>
    </ChartContainer>
  );
}

export {
  ChartContainer,
  LineChartWidget,
  BarChartWidget,
  AreaChartWidget,
  CHART_COLORS,
};
