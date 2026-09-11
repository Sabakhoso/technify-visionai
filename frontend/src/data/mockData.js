import { Video, ShieldCheck, Users, Car, Database } from "lucide-react";

export const statCards = [
  {
    id: "cameras",
    label: "Total Cameras",
    value: "128",
    sub: [
      { text: "Online", color: "text-gray-500" },
      { text: "112", color: "text-brand-blue font-semibold" },
    ],
    icon: Video,
    bg: "bg-brand-blue-light",
    iconColor: "text-brand-blue",
  },
  {
    id: "events",
    label: "Active Events",
    value: "16",
    sub: [
      { text: "Critical", color: "text-gray-500" },
      { text: "3", color: "text-severity-critical font-semibold" },
    ],
    icon: ShieldCheck,
    bg: "bg-brand-green-light",
    iconColor: "text-brand-green",
  },
  {
    id: "people",
    label: "People Detected",
    value: "247",
    sub: [{ text: "Today", color: "text-brand-orange font-medium" }],
    icon: Users,
    bg: "bg-brand-orange-light",
    iconColor: "text-brand-orange",
  },
  {
    id: "vehicles",
    label: "Vehicles Detected",
    value: "89",
    sub: [{ text: "Today", color: "text-brand-purple font-medium" }],
    icon: Car,
    bg: "bg-brand-purple-light",
    iconColor: "text-brand-purple",
  },
  {
    id: "storage",
    label: "Storage Used",
    value: "2.4 TB",
    sub: [{ text: "of 10 TB", color: "text-gray-500" }],
    icon: Database,
    bg: "bg-brand-cyan-light",
    iconColor: "text-brand-cyan",
  },
];

export const liveCameras = [
  {
    id: "CAM-017",
    name: "Main Gate",
    live: true,
    image: "https://picsum.photos/seed/maingate/600/400",
  },
  {
    id: "CAM-082",
    name: "Parking Area",
    live: true,
    image: "https://picsum.photos/seed/parking/600/400",
  },
  {
    id: "CAM-034",
    name: "Building Entrance",
    live: true,
    image: "https://picsum.photos/seed/entrance/600/400",
  },
  {
    id: "CAM-101",
    name: "Corridor 1st Floor",
    live: true,
    image: "https://picsum.photos/seed/corridor/600/400",
  },
];

export const recentAlerts = [
  {
    id: 1,
    title: "Intrusion Detected",
    camera: "CAM-017",
    location: "Main Gate",
    time: "02:13 AM",
    severity: "Critical",
    icon: "intrusion",
    thumb: "https://picsum.photos/seed/alert1/120/80",
  },
  {
    id: 2,
    title: "Restricted Zone Entry",
    camera: "CAM-082",
    location: "Parking Area",
    time: "02:08 AM",
    severity: "High",
    icon: "zone",
    thumb: "https://picsum.photos/seed/alert2/120/80",
  },
  {
    id: 3,
    title: "Object Left Behind",
    camera: "CAM-034",
    location: "Building Entrance",
    time: "01:59 AM",
    severity: "Medium",
    icon: "object",
    thumb: "https://picsum.photos/seed/alert3/120/80",
  },
  {
    id: 4,
    title: "Crowd Detected",
    camera: "CAM-101",
    location: "Corridor 1st Floor",
    time: "01:45 AM",
    severity: "Medium",
    icon: "crowd",
    thumb: "https://picsum.photos/seed/alert4/120/80",
  },
  {
    id: 5,
    title: "Vehicle in Restricted Zone",
    camera: "CAM-023",
    location: "Service Area",
    time: "01:32 AM",
    severity: "Low",
    icon: "vehicle",
    thumb: "https://picsum.photos/seed/alert5/120/80",
  },
];

export const eventsOverview = [
  { id: "all", label: "All Events", value: 247, color: "#2563eb", data: [4, 6, 5, 8, 7, 9, 8] },
  { id: "critical", label: "Critical", value: 3, color: "#dc2626", data: [1, 2, 1, 3, 2, 3, 2] },
  { id: "high", label: "High", value: 8, color: "#ea580c", data: [3, 4, 5, 4, 6, 5, 7] },
  { id: "medium", label: "Medium", value: 21, color: "#ca8a04", data: [5, 7, 6, 8, 7, 9, 8] },
  { id: "low", label: "Low", value: 215, color: "#16a34a", data: [8, 10, 9, 12, 11, 13, 12] },
];

export const topCameras = [
  { id: "CAM-017", name: "Main Gate", events: 23, max: 23 },
  { id: "CAM-082", name: "Parking Area", events: 18, max: 23 },
  { id: "CAM-034", name: "Building Entrance", events: 15, max: 23 },
  { id: "CAM-101", name: "Corridor 1st Floor", events: 11, max: 23 },
  { id: "CAM-023", name: "Service Area", events: 7, max: 23 },
];

export const systemStatus = [
  { id: "ai-engine", label: "AI Engine", status: "Operational", icon: "cpu" },
  { id: "storage", label: "Storage", status: "Operational", icon: "storage" },
  { id: "network", label: "Network", status: "Operational", icon: "network" },
  { id: "cameras", label: "Cameras", status: "112 / 128 Online", icon: "camera", highlight: true },
  { id: "database", label: "Database", status: "Operational", icon: "database" },
];
