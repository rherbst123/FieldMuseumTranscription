from comparison_and_accuracy import Comparison

class PartialComparison(Comparison):

    def compare_and_tally(self, transcription_values_dicts, master_comparison_dict):
        tallies = {"matchValid": 0, "matchNonValid": 0, "noMatchValid": 0, "noMatchNonValid": 0, "gradedMatchValid": 0, "gradedNoMatchValid": 0}
        run_errors = []
        for record_ref, transcription_values_dict, target_values_dict in zip(self.RECORD_REFS, transcription_values_dicts, self.target_values_dicts):
            for fieldname in self.fieldnames:
                target_val = target_values_dict[fieldname]
                transcription_val = transcription_values_dict[fieldname]
                if transcription_val.strip() in ["", "PASS", "unsure and check", "[precise locality unknown]"]:
                    continue  # Just in case the LLM doesn't hazard a guess,
                                    # or there are gaps in some of the fields of observed values.
                                    # This is used when runs are compared for agreement
                                        #  and only agreed values are to be compared against true values
                
                field_comparison_dict = self.get_comparisons(fieldname, transcription_val, target_val, record_ref)
                tallies, master_comparison_dict = self.update_tallies(tallies, field_comparison_dict, master_comparison_dict)
                run_errors += [self.get_errors(field_comparison_dict)]
        return master_comparison_dict, tallies, run_errors 

if __name__ == "__main__":
    
    ###########################################################
    # copy in the name of the configuration file to be used below
    config_filename = "18-mixed-trillo-gpt-4o.yaml" 
    ###########################################################
    CONFIG_PATH = "DataAnalysis/AnalysisTools/Configurations/"
    configuration = PartialComparison.read_configuration_from_yaml(CONFIG_PATH, config_filename)
    accuracy_run = PartialComparison(configuration, config_source=config_filename)
    accuracy_run.run()    
