import React from "react";
import { createRoot } from "react-dom/client";  // Вірний імпорт
import Dashboard from "./components/dashboard";
import "./App.css";

class App extends React.Component {
  render() {
    return (
      <div className="AppContainer">
        <Dashboard />
      </div>
    );
  }
}

// Знаходимо DOM елемент за id "root"
const root = createRoot(document.getElementById("root"));

// Відображаємо компоненту
root.render(<App />);
