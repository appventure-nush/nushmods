import { Module } from "@/types/module";


export async function getModules(): Promise<Module[]> {
  return Promise.resolve([
    {
      code: 'CS1131',
      title: 'Computational Thinking',
      description: 'Sample Description 1',
      mcs: 2,
      hours: 1.5,
    }, {
      code: 'CS2231',
      title: 'Introduction to Programming',
      description: 'Sample Description 2',
      mcs: 2,
      hours: 2,
    }, {
      code: 'CS3231',
      title: 'Object Oriented Programming I',
      description: 'Sample Description 3',
      mcs: 1,
      hours: 1.5,
    }, {
      code: 'CS4231',
      title: 'Introduction to Programming',
      description: 'Sample Description 2',
      mcs: 9,
      hours: 1.5,
    }, {
      code: 'CS5231',
      title: 'Object Oriented Programming I',
      description: 'Sample Description 3',
      mcs: 2,
      hours: 1.5,
    }, {
      code: 'CS6231',
      title: 'Introduction to Programming',
      description: 'Sample Description 2',
      mcs: 2,
      hours: 3.5,
    }, {
      code: 'CS7231',
      title: 'Object Oriented Programming I',
      description: 'Sample Description 3',
      mcs: 2,
      hours: 1.5,
    }, {
      code: 'CS8231',
      title: 'Introduction to Programming',
      description: 'Sample Description 2',
      mcs: 2,
      hours: 1.5,
    }, {
      code: 'CS9231',
      title: 'Object Oriented Programming I',
      description: 'Sample Description 3',
      mcs: 2,
      hours: 1.5,
    }
  ]);
}