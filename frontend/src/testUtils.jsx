import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Shared test helper: components under test use React Query hooks
// (useQuery/useMutation), which require a QueryClientProvider ancestor.
// A fresh QueryClient per render keeps each test's cache isolated.
export function renderWithProviders(ui, { route = "/", initialEntries } = {}) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries ?? [route]}>{ui}</MemoryRouter>
    </QueryClientProvider>,
  );
}
