export default function ProgressBar({ value = 0 }) {
  return (
    <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
      <div className="bg-black h-2" style={{ width: `${Math.min(100, Math.max(0, value))}%` }} />
    </div>
  )
}


