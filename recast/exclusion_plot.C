using namespace std;

// Exclusion plot for paper -- arXiv:1907.04346v2


void exclusion_plot () {


    vector<vector<vector<float>>> var_col_files;

    string str;
    string token;
    int clm = 0;
    char tab = '\t';
    int pos = 0;
    int it = 0;

    // Read all files in a directory
    
    vector<TString> files_names;
    
    TString dirname("data_points/");
    const char *ext=".txt";
    
    TSystemDirectory dir(dirname.Data(), dirname.Data());
    TList *files = dir.GetListOfFiles();
    
    cout << "==> Reading all files ...." << endl;
    
    if (files) {
        TSystemFile *file;
        TString fname;
        TIter next(files);
        while ((file=(TSystemFile*)next())) {
            fname = file->GetName();
            if (!file->IsDirectory() && fname.EndsWith(ext)) {
                cout << fname.Data() << endl;
                files_names.push_back(fname);
            
                 }
            
             }
        
    }
    
    
    
    // read points
    
    
    for (int i = 0; i < files_names.size(); i++ ){
    
        ifstream infile((dirname + files_names[i]).Data());
    
    if (!infile.is_open()) {
        
         cout << "==> Error in opening file !!" << endl;
         exit(EXIT_FAILURE);
     }
    
     vector<vector<float>> var_col;
     var_col.resize(4, vector<float>());

     string line;
       
    while (getline(infile, line)){

        istringstream iss(line);
       
        while (iss >> token){

              
              pos = token.find(tab);
              str = token;
            
            if(pos != -1){
                
               str.erase(pos);
                
            }
           
            var_col[clm].push_back(stof(str));
              
                clm ++;
                
    
          }
        
    iss.clear();
    clm = 0;
    it ++;
        
    }
    
   var_col_files.push_back(var_col);
   infile.close();
        
    }
    
    
TGraph *graph[files_names.size()];
    
    for (int i=0; i < files_names.size(); i++)
            graph[i] = new TGraph();

TMultiGraph *mg = new TMultiGraph();
    
for (int j = 0; j < (int) (files_names).size(); j++){
    
   for(int i = 0; i < (int) (var_col_files[j][0]).size(); i++ ) {
  
       graph[j] -> SetPoint(i, var_col_files[j][0][i], var_col_files[j][1][i]);
       
       cout << "points: " << var_col_files[j][0][i] << " " << var_col_files[j][0][i] << endl;
  
       }
        
    }
    
    
    //plot points
    
    gStyle->SetOptStat(0);
    
    TCanvas * c = new TCanvas ("c", "Parameter space", 100, 200, 700, 500);
    
    c -> SetLogx();
    
    auto legend = new TLegend(0.1,0.7,0.48,0.9);
    
    legend->SetBorderSize(0);
   
    graph[2]->SetLineColor(4);
    graph[2]->SetLineWidth(1);
    graph[2] -> SetLineStyle(1);
    graph[2]->SetFillColorAlpha(kBlue, 0.35);
            
  
    graph[0]->SetLineColor(1);
    graph[0]->SetLineWidth(2);
    graph[0] -> SetLineStyle(1);
    graph[0]->SetFillStyle(3315);

 
    
    graph[1]->SetLineColor(8);
    graph[1]->SetLineWidth(2);
    graph[1] -> SetLineStyle(9);
    graph[1]->SetFillColorAlpha(kWhite, 0.1);
 
    
    graph[3]->SetLineColor(kOrange+1);
    graph[3]->SetLineWidth(2);
    graph[3] -> SetLineStyle(1);
    graph[3]->SetFillColorAlpha(kWhite, 0.1);
  
    
    graph[4]->SetLineColor(2);
    graph[4]->SetLineWidth(2);
    graph[4] -> SetLineStyle(1);
    graph[4]->SetFillColorAlpha(kWhite, 0.1);

    
    mg->Add(graph[0]);
    mg->Add(graph[1]);
    mg->Add(graph[2]);
    mg->Add(graph[3]);
    mg->Add(graph[4]);
    
    mg->SetTitle("e_{d} = 0.4, g = 1.0, m_{#pi} = 4 GeV");
    
    
    
    legend->AddEntry(graph[0],"Di-jet","l");
    legend->AddEntry(graph[1],"Displaced","l");
    legend->AddEntry(graph[2],"Direct searches","l");
    legend->AddEntry(graph[3],"M_{T} sys = 0%","l");
    legend->AddEntry(graph[4],"M_{T} sys = 1%","l");



    c -> cd();
    mg->Draw("AFL");
    mg->GetXaxis()->SetRangeUser(500., 5000.);
    mg->GetYaxis()->SetRangeUser(0., 0.3);
    mg->GetYaxis()->SetTitle("g_{q}");
    mg->GetXaxis()->SetTitle("M_{Z'}");
    
    legend->Draw();
   
    
}
