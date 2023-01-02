import { Module } from "@/types/module";
import { Department } from "@/types/department";


export async function getModules(): Promise<Module[]> {
  return Promise.resolve([
    {
      code: 'CS1131',
      department: 'EL',
      title: 'Computational Thinking',
      description: 'Sample Description 1',
      mcs: 2,
      hours: 1.5,
    }, {
      code: 'CS2231',
      department: 'CS',
      title: 'Introduction to Programming',
      description: 'Sample Description 2',
      mcs: 2,
      hours: 2,
    }, {
      code: 'CS3231',
      department: 'CS',
      title: 'Object Oriented Programming I',
      description: 'Sample Description 3',
      mcs: 1,
      hours: 1.5,
    }, {
      code: 'CS4231',
      department: 'CS',
      title: 'Introduction to Programming',
      description: 'Sample Description 2',
      mcs: 9,
      hours: 1.5,
    }, {
      code: 'CS5231',
      department: 'CS',
      title: 'Object Oriented Programming I',
      description: 'Sample Description 3',
      mcs: 2,
      hours: 1.5,
    }, {
      code: 'CS6231',
      department: 'CS',
      title: 'Introduction to Programming',
      description: 'Sample Description 2',
      mcs: 2,
      hours: 3.5,
    }, {
      code: 'CS7231',
      department: 'CS',
      title: 'Object Oriented Programming I',
      description: 'Sample Description 3',
      mcs: 2,
      hours: 1.5,
    }, {
      code: 'CS8231',
      department: 'CS',
      title: 'Introduction to Programming',
      description: 'Sample Description 2',
      mcs: 2,
      hours: 1.5,
    }, {
      code: 'CS9231',
      department: 'CS',
      title: 'Object Oriented Programming I',
      description: 'Sample Description 3',
      mcs: 2,
      hours: 1.5,
    }
  ]);
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