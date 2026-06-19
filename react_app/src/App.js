import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import "./App.css";

import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import MembersList from "./components/MembersList";
import LoansList from "./components/LoansList";
import LoanForm from "./components/LoanForm";
import LoanRepaymentForm from "./components/LoanRepaymentForm";

import RoleRoute from "./components/RoleRoute";

function PrivateRoute({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <Router>
      <div className="App">

        <Routes>

          {/* 🔓 PUBLIC */}
          <Route path="/login" element={<Login />} />

          {/* 🟢 BOTH ADMIN + MEMBER */}
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />

          <Route
            path="/apply-loan"
            element={
              <PrivateRoute>
                <LoanForm />
              </PrivateRoute>
            }
          />

          <Route
            path="/repay-loan"
            element={
              <PrivateRoute>
                <LoanRepaymentForm />
              </PrivateRoute>
            }
          />

          {/* 🟡 ADMIN ONLY ROUTES */}
          <Route
            path="/members"
            element={
              <RoleRoute allowedRoles={["admin"]}>
                <MembersList />
              </RoleRoute>
            }
          />

          <Route
            path="/loans"
            element={
              <RoleRoute allowedRoles={["admin"]}>
                <LoansList />
              </RoleRoute>
            }
          />

        </Routes>
      </div>
    </Router>
  );
}

export default App;
