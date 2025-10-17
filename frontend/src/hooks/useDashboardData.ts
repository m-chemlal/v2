import { useEffect, useState } from "react";
import axios from "axios";
import type { DashboardSummary } from "../types/dashboard";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || __API_BASE_URL__;

export function useDashboardData() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchData() {
      setLoading(true);
      try {
        const response = await axios.get<DashboardSummary>(`${API_BASE_URL}/api/v1/dashboard`);
        if (isMounted) {
          setData(response.data);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError("Unable to load dashboard data");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 10000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return { data, loading, error };
}
