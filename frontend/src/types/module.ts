export interface Module {
  code: string;
  department: string;
  title: string;
  description: string;
  mcs: number;
  hours: number;
}

export interface FilterParams {
  search: string;
  mcsRange: [number, number];
  hoursRange: [number, number];
}

export class Filter {
  params: FilterParams = {
    search: "",
    mcsRange: [0, 10],
    hoursRange: [0, 5]
  };
  check(module: Module): boolean {
    return (
      (module.code.toLowerCase().includes(this.params.search.toLowerCase()) ||
        module.title.toLowerCase().includes(this.params.search.toLowerCase())) &&
      module.mcs >= this.params.mcsRange[0] &&
      module.mcs <= this.params.mcsRange[1] &&
      module.hours >= this.params.hoursRange[0] &&
      module.hours <= this.params.hoursRange[1]
    );
  }
}