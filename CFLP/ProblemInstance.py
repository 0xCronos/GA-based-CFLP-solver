class ProblemInstance:
    """In memory problem instance values
    """

    def __init__(self, dataset_filepath):
        self.n_centers = 0
        self.n_clients = 0
        self.centers_capacities = []
        self.centers_costs = []
        self.clients_demands = []
        self.clients_costs = []

        self.dataset_filepath = dataset_filepath
        self.__data = self.__read_file(dataset_filepath)

        self.__set_amounts()
        self.__set_centers_data()
        self.__set_clients_data()

    def save(self, output_filepath):
        """ save problem instance values inside file """

        with open(output_filepath, 'w+') as data_file:
            data_file.write(self.__parse_param('cli', self.n_clients))
            data_file.write(self.__parse_param('loc', self.n_centers))
            data_file.write(self.__parse_param('FC', self.centers_costs))
            data_file.write(self.__parse_param(
                'ICap', self.centers_capacities))
            data_file.write(self.__parse_param('dem', self.clients_demands))
            data_file.write(self.__parse_param('TC', self.clients_costs))

    def __set_amounts(self):
        """ read amount of clients and centers """

        self.n_centers = int(self.__data[0].split(' ')[0])
        self.n_clients = int(self.__data[0].split(' ')[1])

        self.__data = self.__data[1:]

    def __set_centers_data(self):
        """ read centers capacities and costs of open each center"""

        for line in self.__data[:self.n_centers]:
            capacity = line.split(' ')[0]

            # manually set capacity for cap[a-c].txt problem instances
            if capacity == 'capacity':
                capacity = 8000 if 'capc' not in self.dataset_filepath else 7250

            self.centers_capacities.append(int(capacity))
            self.centers_costs.append(int(line.split(' ')[1].replace('.', '')))

        self.__data = self.__data[self.n_centers:]

    def __set_clients_data(self):
        """ read clients demands and cost of using each center """

        i = 0
        current_client = 1
        while i < len(self.__data):
            self.clients_demands.append(int(self.__data[i]))

            remaining_costs = self.n_centers

            # read clients costs
            client_costs = []
            for j in range(i+1, len(self.__data)):
                line_costs = list(
                    map(
                        lambda x: str(x),
                        self.__data[j].split(' ')
                    )
                )

                client_costs.extend(line_costs)

                remaining_costs = remaining_costs - len(line_costs)

                if remaining_costs == 0:
                    break

            self.clients_costs.append(client_costs)

            current_client += 1

            i += j - i + 1

    def __read_file(self, data_file):
        file = open(data_file, 'r')

        return list(
            map(
                lambda line: line.split('\n')[0].strip(),
                file.readlines()
            )
        )

    def __parse_param(self, parameter_name, value):
        """return a string with parameter name and value with ampl .dat file format

        Args:
            parameter_name (str): parameter name defined in ampl model
            value (str, list): must be str, list or list of lists

        Returns:
            str: string with parameter name and value with ampl .dat file format
        """
        if isinstance(value, list):
            if any(isinstance(el, list) for el in value):  # for lists of lists
                j_indexes = '\t'.join([str(i) for i in range(
                    1, len(value[0])+1)])

                values = ''
                for i in range(len(value)):
                    values += f'{i + 1}\t' + "\t".join(value[i])

                    if i != len(value) - 1:
                        values += '\n'

                return f'param {parameter_name} : {j_indexes} :=\n\n{values};'
            else:  # for lists
                value = '\t'.join(
                    [f'{idx+1} {c}' for idx, c in enumerate(value)])

        return f'param {parameter_name} := {value};\n'  # for single values
