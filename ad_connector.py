import ldap
from ldap.controls import SimplePagedResultsControl

class ADConnector:
    def __init__(self, uri, user, cred, base_dn):
        ldap_instance = ldap.initialize(uri)
        ldap_instance.protocol_version = ldap.VERSION3
        ldap_instance.set_option(ldap.OPT_REFERRALS, 0)
        ldap_instance.simple_bind_s(user, cred)
        self.__ldap_instance = ldap_instance
        self.__base_dn = base_dn
        self.__known_ldap_reps_ctrls = { SimplePagedResultsControl.controlType: SimplePagedResultsControl }
        self.__request_control = SimplePagedResultsControl(criticality=True, size=1000, cookie='')

    def __del__(self):
        self.__ldap_instance.unbind_s()

    def get_groups(self, dns_hostname):
        result = list()
        try:
            computer_dn, computer_obj = self.__get_computer_info(dns_hostname)
            result = self.__get_computer_groups(computer_dn)
            if ('managedBy' in computer_obj):
                user_cn = computer_obj['managedBy'][0].decode('UTF-8')
                user_groups = self.__get_user_groups(user_cn)
                result = list(set(result + user_groups))
        except Exception as e:
            print(e)
        finally:
            return result

    def __get_computer_info(self, dns_hostname):
        search_filter = f'(&(objectClass=computer)(dNSHostName={dns_hostname}))'
        data = self.__get_data(search_filter, ['cn', 'managedBy'])
        if (len(data) < 1):
            raise Exception(f'{dns_hostname} not found')
        dn, obj = data[0]
        return dn, obj

    def __get_computer_groups(self, computer_dn):
        search_filter = f'(&(objectClass=group)(member:1.2.840.113556.1.4.1941:={computer_dn}))'
        data = self.__get_data(search_filter, ['name'])
        result = list(map(lambda item: item[1]['name'][0].decode('UTF-8'), data))
        return result

    def __get_user_groups(self, user_cn):
        search_filter = f'(&(objectClass=group)(member:1.2.840.113556.1.4.1941:={user_cn}))'
        data = self.__get_data(search_filter, ['name'])
        result = list(map(lambda item: item[1]['name'][0].decode('UTF-8'), data))
        return result

    def __get_data(self, search_filter, attr_list):
        ldap_result = self.__ldap_instance.search_ext(
            self.__base_dn, 
            ldap.SCOPE_SUBTREE, 
            search_filter, 
            attr_list,
            serverctrls=[self.__request_control],
        )
        resp_type, resp_data, resp_msgid, decoded_resp_ctrls = self.__ldap_instance.result3(
            ldap_result,
            timeout=-1,
            resp_ctrl_classes=self.__known_ldap_reps_ctrls,
        )
        return resp_data