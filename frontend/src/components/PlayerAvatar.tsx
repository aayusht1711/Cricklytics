"use client";

import { useState, useEffect } from "react";

export const getInitials = (name?: string) => {
  if (!name || typeof name !== "string") return "CR";
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
};

interface PlayerAvatarProps {
  name: string;
  image?: string;
  className?: string;
  textClassName?: string;
  borderClassName?: string;
}

export default function PlayerAvatar({
  name,
  image,
  className = "w-12 h-12",
  textClassName = "text-sm font-black",
  borderClassName = "border border-white/10"
}: PlayerAvatarProps) {
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    setImgError(false);
  }, [image, name]);

  const isDefault = !image || image.includes("default.png") || imgError;
  const initials = getInitials(name);

  if (isDefault) {
    return (
      <div 
        className={`rounded-full bg-gradient-to-br from-emerald-600 via-teal-700 to-slate-900 ${borderClassName} flex items-center justify-center text-white shadow-lg flex-shrink-0 uppercase tracking-widest ${className}`}
      >
        <span className={textClassName}>{initials}</span>
      </div>
    );
  }

  return (
    <div className={`rounded-full overflow-hidden bg-gray-900 ${borderClassName} flex-shrink-0 ${className}`}>
      <img
        src={image}
        alt=""
        onError={() => setImgError(true)}
        className="w-full h-full object-cover"
      />
    </div>
  );
}
