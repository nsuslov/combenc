class Combiner:
    def __init__(self):
        self.__result_classes = {}

    def append_classes(self, input_classes):
        for class_name in input_classes.keys():
            result_class = self.__result_classes.get(class_name, {})
            input_class = input_classes.get(class_name) or {}
            if (result_class.get('sealed', False)):
                continue
            if (result_class.get('merge', False) or input_class.get('merge', False)):
                self.__result_classes[class_name] = self.__merge(result_class, input_class)
                continue
            self.__result_classes[class_name] = input_class
        return self

    def result(self):
        return self.__result_classes

    def __merge(self, obj1, obj2):
        if (isinstance(obj1, dict) and isinstance(obj2, dict)):
            for key in obj2:
                if key in obj1:
                    obj1[key] = self.__merge(obj1[key], obj2[key])
                else:
                    obj1[key] = obj2[key]
            return obj1
        elif (isinstance(obj1, list) and isinstance(obj2, list)):
            return self.__merge_lists_without_duplicates(obj1, obj2)
        else:
            return obj2

    def __merge_lists_without_duplicates(self, list1, list2):
        for item in list2:
            if item not in list1:
                list1.append(item)
        return list1