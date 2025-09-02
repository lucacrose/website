import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

interface Item {
  id: string;
  name: string;
  value: number;
}

function ItemPage() {
  const { itemId } = useParams<{ itemId: string }>();
  const [item, setItem] = useState<Item | null>(null);

  useEffect(() => {
    if (!itemId) return;

    fetch(`http://localhost:5000/api/item/${itemId}`)
      .then(res => res.json())
      .then(data => setItem(data));
  }, [itemId]);

  if (!item) return <p>Loading...</p>;

  return (
    <>
      <h1>{item.name}</h1>
      <p>Value: {item.value}</p>
    </>
  );
}

export default ItemPage;
