from abc import ABC, abstractmethod

class FuntionStrategy(ABC):
    @abstractmethod
    def excute(self, tool):
        pass

class GetCurrentTemperature(FuntionStrategy):
    def excute(self, tool):
        print(f"{tool}")

class FunctionCalling:
    def setStrategy(self, function_name: FuntionStrategy):
        self.function = function_name
    
    def excute(self, tool):
        self.function.excute(tool)

if __name__ == "__main__":
    test = FunctionCalling()
    test.setStrategy(GetCurrentTemperature())
    test.excute("hello")