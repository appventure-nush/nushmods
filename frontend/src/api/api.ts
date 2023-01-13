import { Module } from "@/types/module";
import { Department } from "@/types/department";


export async function getModules(): Promise<Module[]> {
  return Promise.resolve(fetch("/api/modules").then(res => res.json()).then(res => {
    return res as Module[];
  }));
}

export async function getDepartments(): Promise<Department[]> {
  return Promise.resolve(fetch("/api/departments").then(res => res.json()).then(res => {
    return res as Department[];
  }));
}