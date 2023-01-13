import { Module } from "@/types/module";
import { Department } from "@/types/department";


export async function getModules(): Promise<Module[]> {
  return Promise.resolve(fetch("/api/modules").then(res => res.json()).then(res => {
    return res as Module[];
  }));
}

export async function getDepartments(): Promise<Department[]> {
  return Promise.resolve([
    {
      code: 'EL',
      name: 'English Language & Literature',
      description: 'generic department descripion',
      major: false,
    },
    {
      code: 'MA',
      name: 'Mathematics & Statistics',
      description: 'generic department descripion',
      major: false,
    },
    {
      code: 'CS',
      name: 'Computer Science',
      description: 'generic department descripion',
      major: true,
    },
    {
      code: 'CM',
      name: 'Chemistry',
      description: 'generic department descripion',
      major: true,
    },
    {
      code: 'PC',
      name: 'Physics',
      description: 'generic department descripion',
      major: true,
    },
  ]);
}