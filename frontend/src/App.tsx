import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import ItemPage from "./pages/ItemPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/item/:itemId" element={<ItemPage />} />
      </Routes>
    </Router>
  );
}

export default App;
