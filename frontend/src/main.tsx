import { QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { RotasDoApp } from "./App";
import { criarQueryClient } from "./queryClient";
import "./index.css";

const queryClient = criarQueryClient();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <RotasDoApp />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);
