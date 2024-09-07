function [path] = transfer(varargin)
% Function for saving given variables to a transfer file
% for including and automatically updating latex scripts
    path = varargin{1};
    fileID = fopen(path,'w');
    %nargin
    for i = 2:1:nargin
        val = "";
        in = varargin{i};
        if isa(in,"sym") 
            % if it is a symbolic value (e.g. equation or string)
            val = latex(in);
        elseif isa(in,"float")
            % Determine if matrix or scalar
            if size(in) == [1 1] % scalar
                val = string(round(in,4,"significant"));
            else % matrix/vector
                % from https://www.mathworks.com/matlabcentral/fileexchange/80629-matlab-matrix-to-latex-conversion-example
                %% Convert
                % Get matrix dimensions
                m = size(in, 1);
                n = size(in, 2);
                % Create first line
                s = sprintf('  \\begin{pmatrix}  '); % bmatrix and \n in the original. I like pmatrix better :)
                % Add matrix content
                for k = 1:m
                    for l = 1:n
                        s = sprintf('%s %6.3f', s, in(k, l)); % print 3 decimal places, align to 6 characters
                        if l < n
                            s = sprintf('%s &', s);
                        end
                    end
                    if k < m
                        s = sprintf('%s \\cr', s);
                    end
                    s = sprintf('%s  ', s);
                end
                % Add last line
                s = sprintf('%s\\end{pmatrix}', s);
                
                val = s;
            end
        elseif isa(in,"logical")
            if in
                val = "1";
            else
                val = "0";
            end
        else
            val = string(varargin{i});
        end

        nam = inputname(i);
        % i would rather have it with \t than , but cant get it to work in latex
        
        fprintf(fileID,'%s,%s,-,-\n',nam,val);
    end
    fclose(fileID);
end
